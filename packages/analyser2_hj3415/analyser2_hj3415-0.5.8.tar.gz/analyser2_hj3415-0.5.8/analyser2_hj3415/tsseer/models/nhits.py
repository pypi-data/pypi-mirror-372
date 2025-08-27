from __future__ import annotations

from uuid import uuid4
from typing import Any
import os

import pandas as pd
import numpy as np
import torch

from darts import TimeSeries
from darts.utils.likelihood_models import GaussianLikelihood
from darts.models import NHiTSModel
from pytorch_lightning.callbacks import EarlyStopping

from .utils import extend_future_covariates
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')


def extend_covariate_backwards(need_steps: int, target_train: TimeSeries, volume_train: TimeSeries) -> TimeSeries | None:
    """
    target보다 need_steps만큼 이전부터 covariate가 있어야 하면 부족분을 앞쪽으로 패딩해 확장.
    충분하면 원본 volume_train을 그대로 반환.
    """
    need_start = target_train.start_time() - (need_steps - 1) * target_train.freq

    if volume_train.start_time() > need_start:
        delta = volume_train.start_time() - need_start
        step = pd.Timedelta(days=1) if volume_train.freq == "B" else volume_train.freq
        pad_steps = int(delta / step)

        pad_vals = np.full((pad_steps, 1), volume_train.first_value())
        pad_dates = pd.date_range(
            end=volume_train.start_time() - volume_train.freq,
            periods=pad_steps,
            freq=volume_train.freq
        )

        extended_volume_train = TimeSeries.from_times_and_values(
            pad_dates, pad_vals, columns=volume_train.components
        ).append(volume_train)

        return extended_volume_train

    return volume_train


def enough_length(ts: TimeSeries, in_len: int, out_len: int) -> bool:
    """ts 길이가 in_len + out_len 이상이면 True"""
    return len(ts) >= (in_len + out_len)


def train_and_forecast(series_scaler_dict: dict[str, Any],
                       train_val_dict: dict[str, Any]) -> dict[str, Any] | None:
    # NHITS 기반: 한 번의 학습에서 체크포인트로 ‘val_loss 최저’ 가중치 저장→복원
    INPUT_LEN  = 60   # 과거 60일
    OUTPUT_LEN = 15   # 미래 15영업일
    MIN_LEN    = INPUT_LEN + OUTPUT_LEN  # 75
    PRED_STEPS = 60   # 예측 60영업일

    # ---- 분리/스케일된 입력 꺼내기 ----
    target_train = train_val_dict['target_train']
    target_val   = train_val_dict['target_val']

    target_scaled = series_scaler_dict['target_scaled']
    volume_scaled = series_scaler_dict['volume_scaled']

    target_scaler = series_scaler_dict['target_scaler']

    # ---- 길이 검사 ----
    if not all(enough_length(ts, INPUT_LEN, OUTPUT_LEN) for ts in (target_train, target_val)):
        mylogger.warning(
            f"skip training: series shorter than {MIN_LEN} steps "
            f"(train={len(target_train)}, val={len(target_val)})"
        )
        return None

    # ---- covariates 정렬/확장 (학습: 전체, 검증: val 구간) ----
    volume_scaled_backward_extended_full = extend_covariate_backwards(INPUT_LEN, target_scaled, volume_scaled)
    volume_scaled_backward_extended_val  = extend_covariate_backwards(INPUT_LEN, target_val,    volume_scaled)

    if (volume_scaled_backward_extended_full is None or
        volume_scaled_backward_extended_val  is None):
        raise RuntimeError("covariate extension failed (None returned)")

    # (선택) 점검 로그
    def covariate_ok(past, target, in_len, out_len):
        need_start = target.start_time() - in_len * target.freq
        need_end   = target.end_time()
        mylogger.debug(f"cov.start ⩽ {need_start} ? {past.start_time() <= need_start}")
        mylogger.debug(f"cov.end   ≥ {need_end} ? {past.end_time() >= need_end}")
        mylogger.debug(f"freq 동일 ? {past.freq == target.freq}")

    covariate_ok(volume_scaled_backward_extended_full, target_scaled, in_len=INPUT_LEN-1, out_len=OUTPUT_LEN)
    covariate_ok(volume_scaled_backward_extended_val,  target_val,    in_len=INPUT_LEN-1, out_len=OUTPUT_LEN)

    # ---- NaN 검사 ----
    def validate_no_nan_in_series():
        for name, ts in zip(
            ["target_train", "target_val", "target_scaled",
             "volume_scaled_backward_extended_full", "volume_scaled_backward_extended_val"],
            [target_train, target_val, target_scaled,
             volume_scaled_backward_extended_full,   volume_scaled_backward_extended_val],
        ):
            df = ts.to_dataframe()
            nan_mask = df.isna().any(axis=1)
            if nan_mask.any():
                nan_dates = ts.time_index[nan_mask]
                first_five = list(nan_dates[:5])
                raise ValueError(
                    f"{name} contains NaN values "
                    f"(example dates: {first_five} … total {nan_mask.sum()} rows)."
                )
        mylogger.debug("All series are NaN-free")

    validate_no_nan_in_series()

    # ──────────────────────────────────────────────────────────
    # NHITS 모델 (1회 학습, 체크포인트 저장)
    # ──────────────────────────────────────────────────────────
    early_stop = EarlyStopping(monitor="val_loss", patience=int(INPUT_LEN * 0.25), mode="min")

    model_name = f"nhits_{uuid4().hex[:8]}"

    # Lightning 트레이너 kwargs (GPU일 때만 AMP/benchmark 적용)
    trainer_kwargs = {
        "accelerator": "gpu" if torch.cuda.is_available() else "cpu",
        "gradient_clip_val": 1.0,
        "callbacks": [early_stop],
    }
    if torch.cuda.is_available():
        trainer_kwargs["precision"] = "16-mixed"
        trainer_kwargs["benchmark"] = True

    model = NHiTSModel(
        input_chunk_length = INPUT_LEN,
        output_chunk_length= OUTPUT_LEN,
        n_epochs=1000,
        optimizer_kwargs={"lr": 1e-3},
        likelihood=GaussianLikelihood(),
        batch_size=64,
        random_state=42,

        # 아키텍처 기본값 사용(필요시: num_stacks/num_blocks/num_layers/layer_widths 조정)
        # 예: num_stacks=8, num_blocks=1, num_layers=2, layer_widths=256

        model_name=model_name,
        save_checkpoints=True,

        pl_trainer_kwargs=trainer_kwargs,
    )

    # ──────────────────────────────────────────────────────────
    # 학습 (series=전체 스케일 데이터, 검증은 val)
    # ──────────────────────────────────────────────────────────
    model.fit(
        series              = target_scaled,
        past_covariates     = volume_scaled_backward_extended_full,
        val_series          = target_val,
        val_past_covariates = volume_scaled_backward_extended_val,
        verbose=True,
    )

    # ──────────────────────────────────────────────────────────
    # 베스트 체크포인트 로드
    # ──────────────────────────────────────────────────────────
    best_model = NHiTSModel.load_from_checkpoint(
        model_name=model_name,
        best=True,
    )

    # ──────────────────────────────────────────────────────────
    # 예측
    # ──────────────────────────────────────────────────────────
    past_cov_for_pred = extend_future_covariates(
        PRED_STEPS - OUTPUT_LEN,
        volume_scaled_backward_extended_full
    )

    forecast = best_model.predict(
        n               = PRED_STEPS,
        past_covariates = past_cov_for_pred,
        num_samples     = 80,
        show_warnings   = False,
    )

    # ──────────────────────────────────────────────────────────
    # 스케일 복원 & 신뢰구간/평균 산출
    # ──────────────────────────────────────────────────────────
    target_inv   = target_scaler.inverse_transform(target_scaled)
    forecast_inv = target_scaler.inverse_transform(forecast)

    lower_ts = forecast_inv.quantile(0.10)
    upper_ts = forecast_inv.quantile(0.90)
    mean_ts  = forecast_inv.mean()

    return {
        "fcst_mean_ts": mean_ts,
        "actual_ts":    target_inv,
        "lower_ts":     lower_ts,
        "upper_ts":     upper_ts,
    }