import math
from typing import Any


def cal_deviation(v1: float, v2: float) -> float:
    """
    두 값 간의 퍼센트 괴리율(Deviation)을 계산합니다.

    주어진 두 값 간의 상대적 차이를 백분율로 반환합니다.
    기준값(v1)이 0인 경우, 계산은 NaN을 반환합니다.

    매개변수:
        v1 (float): 기준값.
        v2 (float): 비교할 값.

    반환값:
        float: 두 값 간의 퍼센트 괴리율. 기준값이 0인 경우 NaN.
    """
    try:
        deviation = abs((v1 - v2) / v1) * 100
    except ZeroDivisionError:
        deviation = math.nan
    return deviation


def sigmoid_score(deviation, a=1.0, b=2.0) -> float:
    """"
    주어진 괴리율(Deviation)에 대해 Sigmoid 함수를 적용하여 점수를 계산합니다.

    이 함수는 Sigmoid 함수에 로그 변환된 괴리율을 입력으로 사용하며,
    결과를 0에서 100 사이의 점수로 변환합니다. `a`와 `b` 매개변수를 사용하여
    Sigmoid 곡선의 기울기와 x-축 오프셋을 조정할 수 있습니다.

    매개변수:
        deviation (float): 계산할 괴리율 값 (0 이상의 값이어야 함).
        a (float): Sigmoid 곡선의 기울기 조정값. 기본값은 1.0.
        b (float): Sigmoid 곡선의 x-축 오프셋. 기본값은 2.0.

    반환값:
        float: Sigmoid 함수로 변환된 0~100 사이의 점수.
    """
    # 예: x = log10(deviation + 1)
    x = math.log10(deviation + 1)
    s = 1 / (1 + math.exp(-a * (x - b)))  # 0~1 범위
    return s * 100  # 0~100 범위


def date_set(*args: Any) -> list:
    """
    주어진 값들에서 NaN, None, 빈 문자열("")을 제거하고,
    중복 없이 고유한 리스트로 반환합니다.
    """
    def is_valid(x):
        return x not in ("", None) and not (isinstance(x, float) and math.isnan(x))

    # 유효한 값 필터링 후 중복 제거, 순서 유지
    seen = set()
    result = []
    for item in args:
        if is_valid(item) and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def calc_score(recent_price: float, target_price: float) -> int:
    if math.isnan(recent_price) or math.isnan(target_price):
        return 0
    deviation = cal_deviation(recent_price, target_price)
    score = int(sigmoid_score(deviation))
    if recent_price >= target_price:
        score = -score
    return score


def calculate_volatility(values: list[float]) -> float:
    """
    주어진 숫자 리스트의 변동성(Volatility)을 계산합니다.

    변동성은 연속된 값들 간의 절대 차이의 평균으로 정의되며,
    값이 클수록 데이터의 변동 폭이 크다는 것을 의미합니다.

    예:
        values = [10, 12, 9, 11]
        => 변동성 = (|12-10| + |9-12| + |11-9|) / 3 = (2 + 3 + 2) / 3 = 2.33

    매개변수:
        values (list[float]): 평가할 수치 리스트. 2개 이상이어야 의미 있는 결과를 제공합니다.

    반환값:
        float: 계산된 변동성 값. 값이 1개 이하일 경우 0.0 반환.
    """
    if len(values) < 2:
        return 0.0
    return sum(abs(values[i] - values[i - 1]) for i in range(1, len(values))) / (len(values) - 1)


def score_from_threshold(value: float, thresholds: list[tuple[float, int]]) -> int:
    """
    값(value)이 주어진 임계값(thresholds)을 기준으로 몇 점(score)을 받을지 계산합니다.

    thresholds는 (기준값, 점수) 쌍의 리스트이며, value가 기준값 이상일 경우 해당 점수를 반환합니다.
    가장 먼저 만족하는 조건의 점수를 반환하며, 아무 조건도 만족하지 않으면 0점을 반환합니다.

    예:
        value = 12.5
        thresholds = [(20, 50), (15, 40), (10, 30), (5, 15)]
        => 12.5 >= 10 → 30점 반환

    매개변수:
        value (float): 평가할 값.
        thresholds (list[tuple[float, int]]): (기준값, 점수) 형태의 리스트. 내림차순 정렬이 권장됨.

    반환값:
        int: 기준에 따라 계산된 점수.
    """
    for threshold, score in thresholds:
        if value >= threshold:
            return score
    return 0


def grade_from_score(score: int, levels: list[tuple[int, str]]) -> str:
    """
    점수(score)를 기반으로 등급(grade)을 결정합니다.

    levels는 (기준점수, 등급) 형태의 리스트이며, score가 기준점수 이상일 때 해당 등급을 반환합니다.
    가장 먼저 만족하는 조건의 등급을 반환하며, 만족하는 것이 없다면 마지막 등급을 기본값으로 반환합니다.

    예:
        score = 72
        levels = [(90, "A+"), (75, "A"), (55, "B"), (35, "C"), (0, "D")]
        => 72 >= 55 → "B" 반환

    매개변수:
        score (int): 평가 대상 점수.
        levels (list[tuple[int, str]]): (기준점수, 등급) 리스트. 내림차순 정렬이 권장됨.

    반환값:
        str: 평가된 등급 문자열.
    """
    for threshold, grade in levels:
        if score >= threshold:
            return grade
    return levels[-1][1]