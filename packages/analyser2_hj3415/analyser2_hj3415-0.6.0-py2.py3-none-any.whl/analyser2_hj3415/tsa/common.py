import numpy as np
import pandas as pd
from typing import Optional, List
from datetime import date
from dataclasses_json import config
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


def is_up_by_OLS(data: dict) -> bool:
    """
    주어진 데이터의 값들을 날짜 순으로 정렬한 후, 최소제곱법(OLS)을 이용해 선형 회귀 기울기를 계산합니다.
    데이터가 비어있거나 계산에 필요한 데이터 포인트(1개 이하)가 있는 경우에는 추세를 판단할 수 없으므로 False를 반환합니다.

    Parameters:
        data (dict): 날짜(문자열)를 키로, 해당 날짜의 값(숫자)을 값으로 하는 딕셔너리.

    Returns:
        bool: 계산된 기울기가 양수이면 True (우상향 추세), 그렇지 않으면 False.
    """
    if not data:
        # 데이터가 비어있으면 추세를 판단할 수 없음
        return False

    # 1) 날짜(키) 기준 오름차순 정렬
    sorted_dates = sorted(data.keys())
    values = [data[d] for d in sorted_dates]

    # 2) x 축을 0,1,2... 형태로 부여 (날짜 간격을 동일하게 가정)
    x = np.arange(len(values), dtype=float)
    y = np.array(values, dtype=float)

    # 3) 선형 회귀(최소제곱법)로 기울기(slope) 계산
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    # 분자: sum((xi - x_mean) * (yi - y_mean))
    numerator = np.sum((x - x_mean) * (y - y_mean))
    # 분모: sum((xi - x_mean)^2)
    denominator = np.sum((x - x_mean) ** 2)

    if denominator == 0:
        # 데이터가 1개 이하인 경우 등
        return False

    slope = numerator / denominator

    # 4) 기울기가 양수면 "우상향 추세"로 판별
    return bool(slope > 0)


@dataclass
class LSTMGrade:
    """
    LSTM 모델 학습 결과를 평가하기 위한 데이터 클래스.

    속성:
        ticker (str): 주식 티커(symbol).
        train_mse (float): 학습 데이터에 대한 평균 제곱 오차(MSE).
        train_mae (float): 학습 데이터에 대한 평균 절대 오차(MAE).
        train_r2 (float): 학습 데이터에 대한 결정 계수(R²).
        test_mse (float): 테스트 데이터에 대한 평균 제곱 오차(MSE).
        test_mae (float): 테스트 데이터에 대한 평균 절대 오차(MAE).
        test_r2 (float): 테스트 데이터에 대한 결정 계수(R²).
    """
    ticker: str
    train_mse: Optional[float] = None
    train_mae: Optional[float] = None
    train_r2: Optional[float] = None
    test_mse: Optional[float] = None
    test_mae: Optional[float] = None
    test_r2: Optional[float] = None


# ⓐ 단일 Timestamp ↔ ISO-8601 문자열
ts_enc   = lambda ts: ts.isoformat()
ts_dec   = lambda s: pd.Timestamp(s)

# ⓑ Timestamp 리스트 ↔ 문자열 리스트
list_enc = lambda seq: [ts.isoformat() for ts in seq]
list_dec = lambda seq: [pd.Timestamp(s) for s in seq]


@dataclass_json
@dataclass
class ChartPoint:
    """prices 리스트의 각 원소(x, y)를 표현"""
    x: pd.Timestamp = field(metadata=config(encoder=ts_enc, decoder=ts_dec))
    y: Optional[float] = None


@dataclass_json
@dataclass
class ProphetChartData:
    ticker: str

    labels: List[pd.Timestamp] = field(metadata=config(encoder=list_enc, decoder=list_dec))
    prices: List[ChartPoint]
    yhats:  List[ChartPoint]
    yhat_uppers: List[ChartPoint]
    yhat_lowers: List[ChartPoint]

    is_prophet_up: bool


# ISO-8601(YYYY-MM-DD) 포맷으로 직렬화·역직렬화
date_enc = lambda d: d.isoformat()
date_dec = lambda s: date.fromisoformat(s)


@dataclass_json
@dataclass
class LSTMChartData:
    ticker: str

    labels: List[pd.Timestamp] = field(metadata=config(encoder=list_enc, decoder=list_dec))
    prices: List[ChartPoint]
    future_prices: List[ChartPoint]
    grade: LSTMGrade
    num: int
    is_lstm_up: bool


@dataclass_json
@dataclass
class ProphetLatestData:
    ticker: str

    date: date = field(metadata=config(encoder=date_enc, decoder=date_dec))

    price: Optional[float] = None
    yhat: Optional[float] = None
    yhat_upper: Optional[float] = None
    yhat_lower: Optional[float] = None

    trading_action: str = ''
    score: Optional[int] = None