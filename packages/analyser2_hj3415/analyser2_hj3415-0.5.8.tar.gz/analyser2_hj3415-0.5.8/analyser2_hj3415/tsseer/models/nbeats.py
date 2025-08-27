from __future__ import annotations

from uuid import uuid4
from darts.utils.likelihood_models import GaussianLikelihood
from typing import Any

import pandas as pd
from darts.models import NBEATSModel
import torch
import numpy as np
from pytorch_lightning.callbacks import EarlyStopping
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler

from .utils import extend_future_covariates


from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


def extend_covariate_backwards(need_steps: int, target_train: TimeSeries, volume_train: TimeSeries) -> TimeSeries | None:
    """
    target 시계열의 입력 구간을 맞추기 위해, volume covariate가 시작 지점보다 부족한 경우
    앞쪽에 패딩을 추가하여 확장합니다.

    Parameters:
        need_steps (int): 모델 입력 길이 (input_chunk_length 등), target의 시작 시점 이전에 필요한 step 수.
        target_train (TimeSeries): 예측 대상 시계열 (예: 주가).
        volume_train (TimeSeries): 보조 시계열 (예: 거래량) — 앞쪽이 부족할 경우 확장됩니다.

    Returns:
        TimeSeries: 패딩이 추가된 volume_train (확장된 시계열).
        None: 확장이 필요 없는 경우 (이미 충분한 범위 포함).

    Example:
        extended_volume = extend_covariate_backwards(30, close_series, volume_series)
    """
    # target보다 need_steps만큼 이전부터 covariate가 있어야 함
    need_start = target_train.start_time() - (need_steps - 1) * target_train.freq

    # volume이 그보다 늦게 시작하면 부족함 → padding 필요
    if volume_train.start_time() > need_start:
        delta = volume_train.start_time() - need_start

        step = pd.Timedelta(days=1) if volume_train.freq == "B" else volume_train.freq
        # step = pd.Timedelta(days=1) if str(volume_train.freq) == "B" else volume_train.freq
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

    # padding이 필요 없는 경우
    return volume_train


def enough_length(ts: TimeSeries, in_len: int, out_len: int) -> bool:
    """
    ts 길이가 in_len + out_len 이상이면 True
    """
    return len(ts) >= (in_len + out_len)


def train_and_forecast(series_scaler_dict: dict[str, Any],
                       train_val_dict: dict[str, Any]) -> dict[str, Any] | None:
    # 두 단계 학습(탐색→재학습)을 없애고, 한 번의 학습에서 체크포인트로 ‘val_loss 최저’ 가중치를 저장→복원해 바로 예측에 쓰도록 고친 코드
    INPUT_LEN  = 60   # 과거 60일
    OUTPUT_LEN = 15   # 미래 15영업일
    MIN_LEN    = INPUT_LEN + OUTPUT_LEN  # 75
    PRED_STEPS = 60   # 예측 60영업일

    # ---- 분리/스케일된 입력 꺼내기 ----
    target_train = train_val_dict['target_train']
    target_val   = train_val_dict['target_val']

    # 전체(스케일된) 학습 대상 — 이번 버전은 1회 학습에서 바로 전체를 사용
    target_scaled = series_scaler_dict['target_scaled']
    volume_scaled = series_scaler_dict['volume_scaled']

    # 역스케일러
    target_scaler = series_scaler_dict['target_scaler']

    # ---- 길이 검사 (train/val 모두 충분해야 함) ----
    if not all(
        enough_length(ts, INPUT_LEN, OUTPUT_LEN)
        for ts in (target_train, target_val)
    ):
        mylogger.warning(
            f"skip training: series shorter than {MIN_LEN} steps "
            f"(train={len(target_train)}, val={len(target_val)})"
        )
        return None

    # ---- covariates 정렬/확장 (학습: 전체, 검증: val 구간) ----
    # 학습용 past covariate: 전체 범위를 target_scaled 기준으로 뒤로 INPUT_LEN만큼 확장
    volume_scaled_backward_extended_full = extend_covariate_backwards(
        INPUT_LEN, target_scaled, volume_scaled
    )
    # 검증용 past covariate: val 구간에 맞춰 동일 스케일로 확장
    volume_scaled_backward_extended_val = extend_covariate_backwards(
        INPUT_LEN, target_val, volume_scaled
    )

    if (volume_scaled_backward_extended_full is None or
        volume_scaled_backward_extended_val  is None):
        raise RuntimeError("covariate extension failed (None returned)")

    # ----(선택) 범위/주기 점검 로그----
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
    # NBEATS 모델 (1회 학습, 체크포인트 저장)
    # ──────────────────────────────────────────────────────────
    early_stop = EarlyStopping(monitor="val_loss", patience=int(INPUT_LEN * 0.25), mode="min")

    # 체크포인트 저장/복원을 위해 model_name 부여
    model_name = f"nbeats_{uuid4().hex[:8]}"

    model = NBEATSModel(
        input_chunk_length = INPUT_LEN,
        output_chunk_length= OUTPUT_LEN,
        generic_architecture=True,
        n_epochs=1000,
        optimizer_kwargs={"lr": 1e-3},
        likelihood=GaussianLikelihood(),
        batch_size=64,
        random_state=42,

        # ✅ 체크포인트 저장 설정
        model_name=model_name,
        save_checkpoints=True,  # 내부적으로 val_loss 기준 체크포인트를 저장

        pl_trainer_kwargs={
            "accelerator": "gpu" if torch.cuda.is_available() else "cpu",
            "gradient_clip_val": 1.0,
            "callbacks": [early_stop],  # ModelCheckpoint는 Darts가 내부에서 생성
        },
    )

    # ──────────────────────────────────────────────────────────
    # 학습 (한 번만): series=전체 스케일 데이터, 검증은 val로
    # ──────────────────────────────────────────────────────────
    model.fit(
        series                 = target_scaled,  # 전체
        past_covariates        = volume_scaled_backward_extended_full,
        val_series             = target_val,
        val_past_covariates    = volume_scaled_backward_extended_val,
        verbose=True,
    )

    # ──────────────────────────────────────────────────────────
    # ✅ 최적(베스트) 가중치 복원
    # ──────────────────────────────────────────────────────────
    # Darts가 저장한 ‘val_loss 최저’ 체크포인트에서 동일 아키텍처 모델을 로드
    best_model = NBEATSModel.load_from_checkpoint(
        model_name=model_name,
        best=True,          # 가장 좋은 체크포인트 선택
        # work_dir=None,    # 별도 작업 디렉터리를 쓰면 지정
    )

    # ──────────────────────────────────────────────────────────
    # 예측
    # ──────────────────────────────────────────────────────────
    # 과거 공변량이 필요할 수 있으므로(반복 예측) 미래 구간까지 길이 보강
    past_cov_for_pred = extend_future_covariates(
        PRED_STEPS - OUTPUT_LEN,  # OUTPUT_LEN씩 굴리는 반복 예측 대비 여유분
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


def train_and_forecast_double_study(series_scaler_dict: dict[str, TimeSeries | Scaler],
                                    train_val_dict: dict[str, TimeSeries | Scaler]) -> dict[str, Any] | None:
    INPUT_LEN = 60  # 과거 60일을 보고
    OUTPUT_LEN = 15  # 미래 15영업일 예측
    MIN_LEN = INPUT_LEN + OUTPUT_LEN  # 75

    # 첫번째 모델학습에 사용
    target_train = train_val_dict['target_train']
    target_val = train_val_dict['target_val']

    # --- 학습·검증 모두 길이 충분한지 미리 검사 ----
    if not all(
            enough_length(ts, INPUT_LEN, OUTPUT_LEN)
            for ts in (target_train, target_val)
    ):
        mylogger.warning(
            f"skip training: series shorter than {MIN_LEN} steps "
            f"(train={len(target_train)}, val={len(target_val)})"
        )
        return None  # ← 학습 스킵

    volume_train_backward_extended = extend_covariate_backwards(INPUT_LEN, target_train, train_val_dict['volume_train'])
    volume_val_backward_extended = extend_covariate_backwards(INPUT_LEN, target_val, train_val_dict['volume_val'])

    # 두번째 모델학습에 사용
    target_scaled = series_scaler_dict['target_scaled']
    volume_scaled_backward_extended = extend_covariate_backwards(INPUT_LEN, target_val, series_scaler_dict['volume_scaled'])

    # 역스케일링에 사용
    target_scaler = series_scaler_dict['target_scaler']

    if volume_train_backward_extended is None or volume_val_backward_extended is None or volume_scaled_backward_extended is None:
        raise Exception

    def covariate_ok(past, target, in_len, out_len):
        """
        학습에 필요한 과거 covariate(past)가 target 시계열에 대해 유효한 범위를 갖는지 검사합니다.

        이 함수는 시계열 예측 모델 (예: NBEATS, RNN, Transformer 등)에서
        past covariate가 주어진 input length (`in_len`) 만큼 과거 데이터를 충분히 가지고 있는지,
        그리고 target 시계열의 전체 구간을 커버하는지를 확인합니다.

        Parameters:
            past (TimeSeries): past covariate 역할을 하는 시계열 (예: 거래량).
            target (TimeSeries): 예측 대상 시계열 (예: 주가).
            in_len (int): 모델이 학습 시 참조할 과거 입력 길이 (input_chunk_length).
            out_len (int): 모델의 예측 길이 (forecast horizon). (현재는 검사에 사용되지 않음)

        Prints:
            - past가 target보다 충분히 이전에서 시작하는지 여부
            - past가 target의 끝까지 도달하는지 여부
            - 두 시계열의 frequency가 같은지 여부

        Example:
            >>> covariate_ok(past, target, in_len=30, out_len=180)
            cov.start ⩽ 2023-06-01 ? True
            cov.end   ≥ 2024-06-20 ? True
            freq 동일 ? True
        """
        need_start = target.start_time() - in_len * target.freq
        need_end   = target.end_time()           # 학습 시 future covariate 필요 없음
        mylogger.debug(f"cov.start ⩽ {need_start} ? {past.start_time() <= need_start}")
        mylogger.debug(f"cov.end   ≥ {need_end} ? {past.end_time() >= need_end}")
        mylogger.debug(f"freq 동일 ? {past.freq == target.freq}")

    covariate_ok(volume_train_backward_extended, target_train, in_len=INPUT_LEN-1, out_len=OUTPUT_LEN)
    covariate_ok(volume_val_backward_extended,   target_val,   in_len=INPUT_LEN-1, out_len=OUTPUT_LEN)
    covariate_ok(volume_scaled_backward_extended, target_val, in_len=INPUT_LEN-1, out_len=OUTPUT_LEN)

    def validate_no_nan_in_series():
        for name, ts in zip(
                ["target_train", "volume_train_backward_extended", "target_val",
                 "volume_val_backward_extended", "target_scaled", "volume_scaled_backward_extended"],
                [target_train, volume_train_backward_extended, target_val,
                 volume_val_backward_extended, target_scaled, volume_scaled_backward_extended],
        ):
            # 1) DataFrame으로 변환
            df = ts.to_dataframe()

            # 2) 행 단위 NaN 검사
            nan_mask = df.isna().any(axis=1)  # <- Boolean Series

            # 3) 하나라도 True가 있으면 예외 발생
            if nan_mask.any():
                nan_dates = ts.time_index[nan_mask]  # NaN 행의 날짜 인덱스
                first_five = list(nan_dates[:5])  # 앞 5개만 미리보기
                raise ValueError(
                    f"{name} contains NaN values "
                    f"(example dates: {first_five} … total {nan_mask.sum()} rows)."
                )

        print("All series are NaN-free")

    validate_no_nan_in_series()

    # ──────────────────────────────────────────────────────────
    # NBEATS 모델 정의
    # ──────────────────────────────────────────────────────────

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=int(INPUT_LEN * 0.5), mode="min"),
        # LearningRateMonitor(logging_interval="epoch") - 로그 필요없다면 주석처리
    ]
    from darts.utils.likelihood_models import GaussianLikelihood
    model_tmp = NBEATSModel(
        input_chunk_length=INPUT_LEN,
        output_chunk_length=OUTPUT_LEN,
        generic_architecture=True,
        n_epochs=1000,  # 넉넉히 주고
        optimizer_kwargs={"lr": 1e-3},
        likelihood=GaussianLikelihood(),
        pl_trainer_kwargs={
            "accelerator": "gpu" if torch.cuda.is_available() else "cpu",
            "gradient_clip_val": 1.0,
            "callbacks": callbacks,
        },
        batch_size=32,
        random_state=42,
    )

    # ──────────────────────────────────────────────────────────
    # 일차 학습 - 적절한 epoch를 찾아내기 위해
    # ──────────────────────────────────────────────────────────
    model_tmp.fit(
        series           = target_train,
        past_covariates  = volume_train_backward_extended,
        val_series       = target_val,
        val_past_covariates = volume_val_backward_extended,
        verbose          = True
    )

    # ──────────────────────────────────────────────────────────
    # 이차 NBEATS 모델 정의
    # ──────────────────────────────────────────────────────────

    # 몇 epoch에서 중단됐는지 확인
    stopped_epoch = max(next(
        cb for cb in model_tmp.model.trainer.callbacks if isinstance(cb, EarlyStopping)
    ).stopped_epoch, 1)
    print(f"Early stopped at: {stopped_epoch} epoch")

    # 전체 데이터를 사용해서 stopped_epoch만큼 학습 (검증 없이)
    final_model = NBEATSModel(
        input_chunk_length=INPUT_LEN,
        output_chunk_length=OUTPUT_LEN,
        generic_architecture=True,
        n_epochs=stopped_epoch,
        optimizer_kwargs={"lr": 1e-3},
        likelihood=GaussianLikelihood(),
        pl_trainer_kwargs={
            "accelerator": "gpu" if torch.cuda.is_available() else "cpu",
            "gradient_clip_val": 1.0,
        },
        batch_size=32,
        random_state=42,
    )

    # ──────────────────────────────────────────────────────────
    # 이차 학습 - 전체 데이터로 실전용 학습
    # ──────────────────────────────────────────────────────────

    final_model.fit(
        series           = target_scaled,
        past_covariates  = volume_scaled_backward_extended,
        verbose          = True,
    )

    # ──────────────────────────────────────────────────────────
    # 예측 (미래 n영업일)
    # ──────────────────────────────────────────────────────────
    PRED_STEPS = 60
    forecast = final_model.predict(
        n              = PRED_STEPS,
        past_covariates= extend_future_covariates(PRED_STEPS-OUTPUT_LEN, volume_scaled_backward_extended),
        num_samples=200,  # ← 샘플 수(50~500 권장)
        show_warnings=False
    )

    # ──────────────────────────────────────────────────────────
    # 스케일 복원 & 평가
    # ──────────────────────────────────────────────────────────
    # 1) 예측을 역스케일한 뒤
    target_inv = target_scaler.inverse_transform(target_scaled)
    forecast_inv = target_scaler.inverse_transform(forecast)

    # 2) 원-스케일에서 바로 통계 계산
    lower_ts = forecast_inv.quantile(0.10)  # 10 퍼센타일
    upper_ts = forecast_inv.quantile(0.90)  # 90 퍼센타일
    mean_ts = forecast_inv.mean()  # 평균 또는 중앙값

    return {
        'fcst_mean_ts': mean_ts,
        'actual_ts': target_inv,
        'lower_ts': lower_ts,
        'upper_ts': upper_ts,
    }