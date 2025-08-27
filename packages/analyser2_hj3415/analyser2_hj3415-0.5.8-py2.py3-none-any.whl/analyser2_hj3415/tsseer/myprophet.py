from typing import Any, Literal
import json
from prophet import Prophet
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .utils import get_raw_data, judge_trend, single_ticker_key_factory, trend_key_factory

from redis_hj3415.wrapper import redis_cached, redis_async_cached
from redis_hj3415.common.connection import get_redis_client_async
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def prepare_data(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    # ── (1) 기본 정리 ────────────────────────────────────
    df.columns = df.columns.get_level_values(0)
    df.index   = df.index.tz_localize(None)
    df = df[['Close', 'Volume']].dropna().reset_index()
    df.columns = ['ds', 'y', 'volume']          # Prophet 규격

    # ── (2) 스케일러 두 개 생성 ─────────────────────────
    volume_scaler = StandardScaler()
    y_scaler      = StandardScaler()

    df['volume_scaled'] = volume_scaler.fit_transform(df[['volume']])
    df['y_scaled']      = y_scaler.fit_transform(df[['y']])

    return {
        'prepared_df'   : df,              # y/raw, y_scaled, volume_scaled 모두 보존
        'volume_scaler' : volume_scaler,
        'y_scaler'      : y_scaler,
    }


def run_forecast(df_scaler_dict: dict[str, object], periods: int = 180) -> pd.DataFrame:
    """Prophet 학습 & periods 일 예측 → 역-스케일링해서 반환"""

    # ── 0. 필요한 객체 꺼내기 ───────────────────────────
    df:            pd.DataFrame   = df_scaler_dict['prepared_df'].copy()
    vol_scaler:    StandardScaler = df_scaler_dict['volume_scaler']
    y_scaler:      StandardScaler = df_scaler_dict['y_scaler']

    # ── 1. Prophet 학습용 DF 생성 (y_scaled만 사용) ────
    prophet_df = (
        df[['ds', 'y_scaled', 'volume_scaled']]
        .rename(columns={'y_scaled': 'y'})
    )

    model = Prophet()
    model.add_regressor('volume_scaled')
    model.fit(prophet_df)

    # ── 2. 미래 데이터프레임 생성 ───────────────────────
    future = model.make_future_dataframe(periods=periods)

    mean_vol = df['volume'].mean()
    future['volume_scaled'] = vol_scaler.transform([[mean_vol]] * len(future))

    # ── 3. 예측 + y 역-스케일링 ─────────────────────────
    pred_df = model.predict(future)

    cols_to_inverse = ['yhat', 'yhat_lower', 'yhat_upper']
    pred_df[cols_to_inverse] = y_scaler.inverse_transform(pred_df[cols_to_inverse])

    # (선택) 학습 구간의 실측 y도 복원해 두면 병합/시각화에 편리
    df['y'] = y_scaler.inverse_transform(df[['y_scaled']])
    # pred_df 와 df 를 나중에 merge 하면 실측·예측을 한 눈에 볼 수 있음

    return pred_df


def latest_anomaly_score(
    df: pd.DataFrame,
    *,
    y_col: str = 'actual',
    lo_col: str = 'lower',
    up_col: str = 'upper',
    ndigits: int = 4,
    eps: float = 1e-9
) -> float | None:
    """
    최근 값이 예측 구간을 얼마나 벗어났는지 비율로 반환.
    - upper 초과 → 양수
    - lower 초과 → 음수
    - 구간 안 → 0
    - 계산 불가 → None
    """
    valid = df.dropna(subset=[y_col, lo_col, up_col])
    if valid.empty:
        return None

    y, lo, up = valid.iloc[-1][[y_col, lo_col, up_col]]

    width = max(up - lo, eps)

    if y > up:
        score = (y - up) / width  # 양수
    elif y < lo:
        score = -(lo - y) / width  # 음수
    else:
        score = 0.0

    return round(score, ndigits)

REDIS_PREFIX_MAP = {
    'prophet': "myprophet_prophet",
    'trend': "myprophet_trend",
}

@redis_cached(prefix=REDIS_PREFIX_MAP['prophet'], key_factory=single_ticker_key_factory)
def prophet_forecast(ticker: str, *, refresh: bool = False, cache_only: bool = False) -> dict[str, Any]:
    df = get_raw_data(ticker)
    df_scaler_dict = prepare_data(df)
    past_and_forecast = run_forecast(df_scaler_dict)

    prepared_df: pd.DataFrame = df_scaler_dict['prepared_df']
    merged = (
        prepared_df[['ds', 'y']]
        .merge(
            past_and_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            on='ds', how='outer'
        )
        .sort_values('ds')
    )

    # ------------- (2) 추세 평가 -------------
    fcst_vals = merged.loc[merged['yhat'].notna(), 'yhat'].values
    trend = judge_trend(fcst_vals, slope_th=0.0005, pct_th=1.0)  # "상승" | "하락" | "횡보" | 미정

    # 3-1) anomaly score 계산
    anomaly = latest_anomaly_score(merged, y_col='y', lo_col='yhat_lower', up_col='yhat_upper')

    return {
        'ds'      : merged['ds'].dt.strftime('%Y-%m-%d').tolist(),
        'actual'  : merged['y'].where(merged['y'].notna()).tolist(),
        'forecast': merged['yhat'].round(2).tolist(),
        'lower'   : merged['yhat_lower'].round(2).tolist(),
        'upper'   : merged['yhat_upper'].round(2).tolist(),
        'trend': trend,
        "anomaly_score": anomaly
    }


@redis_async_cached(prefix=REDIS_PREFIX_MAP['trend'], key_factory=trend_key_factory)
async def filter_prophet_by_trend_and_anomaly(tickers: list[str], trend: Literal["상승", "하락"], *,
                                              refresh: bool = False, cache_only: bool = False) -> list[dict]:
    """
    주어진 종목 목록(`tickers`)에 대해 Redis에 저장된 Prophet 예측 데이터를 기반으로
    지정된 추세(`trend`)와 이상치 점수(`anomaly_score`) 조건을 만족하는 항목만 필터링하여 반환합니다.

    ### 주요 동작
    1. Redis에서 Prophet 예측 데이터 일괄 조회 (`mget`).
    2. 각 종목별로 다음 조건을 만족하는 경우 결과에 포함:
       - 예측된 추세(`payload['trend']`)가 입력한 `trend`와 동일해야 함.
       - 이상치 점수(`anomaly_score`)가 존재해야 함.
       - **상승(`trend="상승"`)**: 이상치 점수가 `-0.01` 이하인 경우만 포함.
       - **하락(`trend="하락"`)**: 이상치 점수가 `0.01` 이상인 경우만 포함.
    3. 최종 결과를 이상치 점수의 절대값 기준 내림차순으로 정렬 후 반환.

    ### 매개변수
    - `tickers (list[str])`:
        필터링할 종목 코드 목록.
    - `trend (Literal["상승", "하락"])`:
        필터링할 목표 추세.
    - `refresh (bool, optional)`:
        캐시 무효화 여부. 기본값은 `False`.
    - `cache_only (bool, optional)`:
        캐시에서만 조회하고 미존재 시 생략 여부. 기본값은 `False`.

    ### 반환값
    - `list[dict]`: 다음 필드를 포함하는 딕셔너리 목록
        ```python
        [
            {
                "ticker": str,          # 종목 코드
                "trend": str,           # 예측 추세 ("상승" 또는 "하락")
                "anomaly_score": float  # 이상치 점수
            },
            ...
        ]
        ```

    ### 예시
    ```python
    results = await filter_prophet_by_trend_and_anomaly(
        tickers=["005930", "000660", "035420"],
        trend="상승"
    )
    # 결과 예시:
    # [
    #   {"ticker": "005930", "trend": "상승", "anomaly_score": -0.05},
    #   {"ticker": "000660", "trend": "상승", "anomaly_score": -0.02},
    # ]
    ```
    """
    r = get_redis_client_async()
    # prophet을 사용해서 데이터를 만들었을 경우
    keys = [f"{REDIS_PREFIX_MAP['prophet']}:{str(t).strip()}" for t in tickers]
    values = await r.mget(keys)
    # print(values)

    rows: list[dict] = []
    for ticker, raw in zip(tickers, values):
        payload: dict | None = json.loads(raw) if raw else None
        if payload is None:
            continue
        if trend != payload['trend']:
            continue
        anomaly_score = payload.get('anomaly_score')
        if anomaly_score is None:
            continue
        if trend == '상승' and anomaly_score <= -0.01:
            rows.append(
                {'ticker': ticker, 'trend': payload['trend'], 'anomaly_score': anomaly_score}
            )
        elif trend == '하락' and anomaly_score >= 0.01:
            rows.append(
                {'ticker': ticker, 'trend': payload['trend'], 'anomaly_score': anomaly_score}
            )
    # ── 핵심: 절대값 기준 내림차순 정렬 ──────────────────
    rows.sort(key=lambda item: abs(item["anomaly_score"]), reverse=True)
    # print(rows)
    return rows

