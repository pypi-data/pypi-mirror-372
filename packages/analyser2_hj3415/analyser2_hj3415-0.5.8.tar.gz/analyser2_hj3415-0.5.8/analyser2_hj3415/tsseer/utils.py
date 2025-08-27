from __future__ import annotations

import numpy as np
from typing import Literal
import datetime
import time
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import hashlib

from darts import TimeSeries

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def get_raw_data(ticker: str, max_retries: int = 3, delay_sec: int = 2) -> pd.DataFrame:
    """
    Yahoo Finance에서 특정 티커의 최근 4년간 주가 데이터를 가져옵니다.

    Args:
        ticker (str): 조회할 종목의 티커 (예: "005930.KQ").
        max_retries (int, optional): 최대 재시도 횟수. 기본값은 3.
        delay_sec (int, optional): 재시도 전 대기 시간 (초). 기본값은 2초.

    Returns:
        pd.DataFrame: 주가 데이터프레임. 실패 시 빈 DataFrame 반환.
    """
    today = datetime.datetime.today()
    four_years_ago = today - datetime.timedelta(days=365 * 4)

    for attempt in range(1, max_retries + 1):
        try:
            data = yf.download(
                tickers=ticker,
                start=four_years_ago.strftime('%Y-%m-%d'),
                # end=today.strftime('%Y-%m-%d')  # 생략 시 최신 날짜까지 자동 포함
            )

            if not data.empty:
                return data
            else:
                print(f"[{attempt}/{max_retries}] '{ticker}' 데이터가 비어 있습니다. {delay_sec}초 후 재시도합니다...")

        except Exception as e:
            print(f"[{attempt}/{max_retries}] '{ticker}' 다운로드 중 오류 발생: {e}. {delay_sec}초 후 재시도합니다...")

        time.sleep(delay_sec)

    mylogger.error(f"'{ticker}' 주가 데이터를 최대 {max_retries}회 시도했지만 실패했습니다.")
    return pd.DataFrame()


def timeseries_to_dataframe(forecast: TimeSeries) -> pd.DataFrame:
    forecast_df = forecast.to_dataframe()
    mylogger.debug(forecast_df)
    return forecast_df


def show_graph(data: dict[str, list]) -> None:
    """
    JSON 직렬화가 가능한 dict( keys = ds, actual, forecast, lower, upper )를
    받아 matplotlib 그래프를 표시한다.

    Parameters
    ----------
    data   : dict
        {"ds": [...], "actual": [...], "forecast": [...], "lower": [...], "upper": [...]}
        * ds        : 날짜 문자열(YYYY-MM-DD)
        * actual    : 실제값. None → 결측
        * forecast  : 예측값(포인트). None → 결측
        * lower/upper : (선택) 예측구간 하한/상한. None → 결측
    """
    # ──────────────────────────────────────
    # ① dict → DataFrame
    # ──────────────────────────────────────
    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(df["ds"])
    df.set_index("ds", inplace=True)

    # 숫자형 변환 (None → NaN)
    for col in ["actual", "forecast", "lower", "upper"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ──────────────────────────────────────
    # ② plot
    # ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 6))

    df["actual"].plot(ax=ax, label="Actual", lw=1.6)
    df["forecast"].plot(ax=ax, label="Forecast", lw=1.6, color="tab:orange")

    # 불확실성 구간이 있으면 음영으로 표시
    if {"lower", "upper"}.issubset(df.columns):
        ax.fill_between(
            df.index,
            df["lower"],
            df["upper"],
            color="tab:orange",
            alpha=0.5,
            label="90% interval",
        )

    ax.set_title("nbeats forecast")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()



def judge_trend(fcst: np.ndarray, slope_th: float = 0.001, pct_th  : float = 2.0) -> Literal["상승", "하락", "횡보", "미정"]:
    fcst = fcst[~np.isnan(fcst)]
    if len(fcst) < 15:          # 데이터가 너무 짧으면
        return "미정"

    x = np.arange(len(fcst))
    slope = np.polyfit(x, fcst, 1)[0] / fcst.mean()   # 상대 기울기(%)
    delta_pct = (fcst[-1] - fcst[0]) / fcst[0] * 100

    if slope >  slope_th and delta_pct >  pct_th:   return "상승"
    if slope < -slope_th and delta_pct < -pct_th:   return "하락"
    return "횡보"


def single_ticker_key_factory(args: tuple, kwargs: dict, prefix: str) -> str:
    # ticker는 포지셔널(첫 번째)로 올 수도, 키워드로 올 수도 있으니 둘 다 처리
    ticker = kwargs.get("ticker")
    if ticker is None:
        ticker = args[0] if args else ""

    # 필요하면 정규화(대소문자 무시)도 가능: ticker = str(ticker).strip().lower()
    return f"{prefix}:{str(ticker).strip()}"



def trend_key_factory(args: tuple, kwargs: dict, prefix: str) -> str:
    """
    키 형식: <prefix>:<trend>:<shaN>
    - tickers: lower/strip → 중복 제거 → 정렬(순서/대소문자 무시)
    - trend  : strip
    - 포지셔널/키워드 혼합을 시그니처에 의존하지 않고 안전히 처리
    """
    # 1) 인자 추출(포지셔널/키워드 모두 지원)
    tickers = kwargs.get("tickers") if "tickers" in kwargs else (args[0] if len(args) > 0 else [])
    trend   = kwargs.get("trend")   if "trend"   in kwargs else (args[1] if len(args) > 1 else "")

    # 2) 정규화
    norm_tickers = sorted({str(t).strip().lower() for t in (tickers or [])})
    trend_norm   = str(trend).strip()

    # 3) 해시(키 길이 때문에 축약; 대량 조합이면 16자리 권장)
    sha = hashlib.sha1(",".join(norm_tickers).encode("utf-8")).hexdigest()[:8]   # 짧게(8)

    return f"{prefix}:{trend_norm}:{sha}"