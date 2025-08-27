import math
import re

import numpy as np
import pandas as pd
from analyser2_hj3415.fscore.utils import mongo_utils, math_utils
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


"""
- 각분기의 합이 연이 아닌 타이틀(즉 sum_4q를 사용하면 안됨)
'*(지배)당기순이익'
'*(비지배)당기순이익'
'장기차입금'
'현금및예치금'
'매도가능금융자산'
'매도파생결합증권'
'만기보유금융자산'
'당기손익-공정가치측정금융부채'
'당기손익인식(지정)금융부채'
'단기매매금융자산'
'단기매매금융부채'
'예수부채'
'차입부채'
'기타부채'
'보험계약부채(책임준비금)'
'*CAPEX'
'ROE'
"""

"""
- sum_4q를 사용해도 되는 타이틀
'자산총계'
'당기순이익'
'유동자산'
'유동부채'
'비유동부채'

'영업활동으로인한현금흐름'
'재무활동으로인한현금흐름'
'ROIC'
"""


def calc_당기순이익(c103재무상태표q: pd.DataFrame, c103손익계산서q: pd.DataFrame, c103재무상태표y: pd.DataFrame) -> tuple[str, float]:
    """
    지배주주 당기순이익을 계산합니다.

    1. 우선 '*(지배)당기순이익' 값이 있는지 확인합니다.
    2. 값이 없으면 다음 식으로 수동 계산합니다:
       최근 4분기 '당기순이익' 합계 - '*(비지배)당기순이익'

    Args:
        c103재무상태표q (pd.DataFrame): 분기별 재무상태표
        c103손익계산서q (pd.DataFrame): 분기별 손익계산서
        c103재무상태표y (pd.DataFrame): 연간 재무상태표

    Returns:
        tuple[str, float]:
            - 날짜 (str): 가장 최근의 유효한 날짜. 없으면 빈 문자열 반환
            - 지배주주 당기순이익 (float): 계산된 값. 모든 값이 NaN일 경우 NaN 반환
    """
    d, 지배당기순이익 = mongo_utils.get_latest_valid_value(c103재무상태표q, '*(지배)당기순이익')
    mylogger.debug(f"*(지배)당기순이익: {지배당기순이익} - {d}")

    if math.isnan(지배당기순이익):
        mylogger.warning(f"(지배)당기순이익이 없는 종목. 수동으로 계산합니다.")
        최근4분기당기순이익 = mongo_utils.sum_of_row(c103손익계산서q, '당기순이익')
        mylogger.debug(f"최근4분기당기순이익 : {최근4분기당기순이익}")
        d2, 비지배당기순이익 = mongo_utils.get_latest_valid_value(c103재무상태표y, '*(비지배)당기순이익')
        mylogger.debug(f"비지배당기순이익y : {비지배당기순이익}")
        # 가변리스트 언패킹으로 하나의 날짜만 사용하고 나머지는 버린다.
        # 여기서 *_는 “나머지 값을 다 무시하겠다”는 의미
        try:
            date, *_ = math_utils.date_set(d, d2)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''
        계산된지배당기순이익 = round(float(np.nansum([최근4분기당기순이익, -비지배당기순이익])), 1)
        mylogger.debug(f"계산된 지배당기순이익 : {계산된지배당기순이익}")
        return date, 계산된지배당기순이익
    else:
        return d, 지배당기순이익


def _calc_by_manual_items(c103재무상태표q: pd.DataFrame, row_names: list[str], label: str) -> tuple[str, float]:
    """
    여러 항목 값을 수동으로 더해서 계산하는 유틸 함수.

    Args:
        c103재무상태표q (pd.DataFrame): 대상 데이터프레임
        row_names (list[str]): 수동 계산에 사용할 항목 이름 리스트
        label (str): 로그 출력용 라벨

    Returns:
        tuple[str, float]: (가장 최신 날짜, 계산된 합계)
    """
    mylogger.warning(f"{label}이 없어 수동 계산합니다.")
    dates_vals = [
        mongo_utils.get_latest_valid_value(c103재무상태표q, name) for name in row_names
    ]
    dates_vals = [(d, v) for d, v in dates_vals if pd.notna(v)]

    if not dates_vals:
        mylogger.warning(f"{label} 수동 계산 항목 모두 NaN.")
        return '', 0.0

    dates, values = zip(*dates_vals)
    try:
        date, *_ = math_utils.date_set(*dates)
    except ValueError:
        date = ''
        mylogger.warning("유효한 날짜가 없어 빈 문자열 처리.")

    total = round(float(np.nansum(values)), 1)
    mylogger.debug(f"계산된 {label}: {total}")
    return date, total


def calc_유동부채(c103재무상태표q: pd.DataFrame) -> tuple[str, float]:
    val = mongo_utils.sum_of_row(c103재무상태표q, '유동부채')
    if not pd.isna(val):
        return '', val
    return _calc_by_manual_items(
        c103재무상태표q,
        ['당기손익인식(지정)금융부채', '당기손익-공정가치측정금융부채', '매도파생결합증권', '단기매매금융부채'],
        '유동부채'
    )


def calc_비유동부채(c103재무상태표q: pd.DataFrame) -> tuple[str, float]:
    val = mongo_utils.sum_of_row(c103재무상태표q, '비유동부채')
    if not pd.isna(val):
        return '', val
    return _calc_by_manual_items(
        c103재무상태표q,
        ['예수부채', '보험계약부채(책임준비금)', '차입부채', '기타부채'],
        '비유동부채'
    )


def calc_유동자산(c103재무상태표q: pd.DataFrame) -> tuple[str, float]:
    val = mongo_utils.sum_of_row(c103재무상태표q, '유동자산')
    if not pd.isna(val):
        return '', val
    return _calc_by_manual_items(
        c103재무상태표q,
        ['현금및예치금', '단기매매금융자산', '매도가능금융자산', '만기보유금융자산'],
        '유동자산'
    )


def calc_주주수익률(c103현금흐름표q: pd.DataFrame, 시가총액_억: float) -> float:
    """
    재무활동현금흐름과 시가총액을 기반으로 주주수익률을 계산합니다.

    반환값:
        - 주주수익률 (float): 주주 수익률 (%)
    """
    재무활동현금흐름 = mongo_utils.sum_of_row(c103현금흐름표q, '재무활동으로인한현금흐름')
    try:
        주주수익률 = round((재무활동현금흐름 / 시가총액_억 * -100), 2)
    except ZeroDivisionError:
        주주수익률 = np.nan
        mylogger.warning(f'시가총액 0으로 나눔 오류. 재무활동현금흐름: {재무활동현금흐름}')
    return 주주수익률


def calc_이익지표(c103현금흐름표q: pd.DataFrame, 시가총액_억: float, 당기순이익: float) -> float:
    """
    (당기순이익 - 영업활동현금흐름) 대비 시가총액 비율을 계산한 '이익지표'를 반환합니다.

    반환값:
        float: 이익지표

    주의:
        이 지표는 일반적인 ROE/ROIC와는 달리,
        이익과 현금 흐름의 차이를 시장 가치 기준으로 본 분석용 지표입니다.
    """
    영업활동현금흐름 = mongo_utils.sum_of_row(c103현금흐름표q, '영업활동으로인한현금흐름')

    if 시가총액_억 is None or 시가총액_억 == 0 or math.isnan(시가총액_억):
        mylogger.warning(f"시가총액이 0 또는 NaN입니다: {시가총액_억}")
        return np.nan

    try:
        이익지표 = round(((당기순이익 - 영업활동현금흐름) / 시가총액_억) * 100, 2)
    except Exception as e:
        mylogger.warning(f'이익지표 계산 실패: {e}')
        이익지표 = np.nan

    return 이익지표


def _extract_year(key: str) -> int:
    match = re.match(r"(\d{4})", key)
    return int(match.group(1)) if match else 0


def evaluate_roic(roic_dict: dict[str, float]) -> dict:
    if not roic_dict:
        return {"평균": 0.0, "변동성": 0.0, "점수": 0, "등급": "N/A"}

    sorted_data = sorted(roic_dict.items(), key=lambda x: _extract_year(x[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    avg = sum(values) / len(values)
    vol = math_utils.calculate_volatility(values)

    score = 0
    score += math_utils.score_from_threshold(avg, [(20, 50), (15, 40), (10, 30), (5, 15)])
    score += math_utils.score_from_threshold(vol, [(0, 30), (2, 20), (5, 10)])
    score += math_utils.score_from_threshold(len(values), [(5, 20), (3, 10)])

    grade = math_utils.grade_from_score(score, [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (보통)"), (30, "C (불안정)"), (0, "D (위험)")])

    return {"평균": round(avg, 2), "변동성": round(vol, 2), "점수": score, "등급": grade}


def evaluate_roe(roe_data: dict[str, float], debt_data: dict[str, float], equity_data: dict[str, float]) -> dict:
    common_keys = sorted(set(roe_data) & set(debt_data) & set(equity_data), key=_extract_year)
    if not common_keys:
        return {"평균": 0.0, "변동성": 0.0, "평균부채비율": 0.0, "자기자본증가율": 0.0, "점수": 0, "등급": "N/A"}

    roe_vals = [roe_data[k] for k in common_keys]
    debt_vals = [debt_data[k] for k in common_keys]
    equity_vals = [equity_data[k] for k in common_keys]

    avg_roe = sum(roe_vals) / len(roe_vals)
    volatility = math_utils.calculate_volatility(roe_vals)
    avg_debt = sum(debt_vals) / len(debt_vals)
    equity_growth = ((equity_vals[-1] - equity_vals[0]) / equity_vals[0] * 100) if equity_vals[0] != 0 else 0

    score = 0
    score += math_utils.score_from_threshold(avg_roe, [(20, 40), (15, 30), (10, 20), (5, 10)])
    score += math_utils.score_from_threshold(volatility, [(0, 20), (2, 15), (5, 10)])
    score += math_utils.score_from_threshold(avg_debt, [(0, 20), (50, 15), (100, 10)])
    score += math_utils.score_from_threshold(equity_growth, [(30, 10), (10, 5)])
    score += math_utils.score_from_threshold(len(common_keys), [(5, 10), (3, 5)])

    grade = math_utils.grade_from_score(score, [(90, "A+ (탁월)"), (75, "A (우수)"), (55, "B (보통)"), (35, "C (불안정)"), (0, "D (위험)")])

    return {
        "평균": round(avg_roe, 2),
        "변동성": round(volatility, 2),
        "평균부채비율": round(avg_debt, 2),
        "자기자본증가율": round(equity_growth, 2),
        "점수": score,
        "등급": grade
    }


def evaluate_roa(roa_data: dict[str, float], asset_data: dict[str, float] | None = None) -> dict:
    if not roa_data:
        return {
            "평균": 0.0, "변동성": 0.0, "점수": 0, "등급": "N/A",
            "추세": "하락", "자산증가": False
        }

    sorted_data = sorted(roa_data.items(), key=lambda x: _extract_year(x[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    avg = sum(values) / len(values)
    vol = math_utils.calculate_volatility(values)
    trend = values[-1] - values[0] if len(values) >= 2 else 0

    asset_increase = False
    if asset_data:
        asset_values = [asset_data.get(k, 0) for k, _ in sorted_data]
        if len(asset_values) >= 2:
            asset_increase = asset_values[-1] > asset_values[0]

    score = 0
    score += math_utils.score_from_threshold(avg, [(10, 50), (7, 40), (5, 30), (3, 15)])
    score += math_utils.score_from_threshold(vol, [(0, 25), (1.5, 15), (3, 8)])
    score += 15 if trend > 0 else 7 if trend == 0 else 0
    score += 10 if asset_increase else 0

    grade = math_utils.grade_from_score(score, [(90, "A+ (탁월)"), (70, "A (우수)"), (50, "B (보통)"), (30, "C (불안정)"), (0, "D (위험)")])

    return {
        "평균": round(avg, 2),
        "변동성": round(vol, 2),
        "점수": score,
        "등급": grade,
        "추세": "상승" if trend > 0 else "보합" if trend == 0 else "하락",
        "자산증가": asset_increase
    }


def calc_투자수익률(c103재무상태표y: pd.DataFrame, c104q: pd.DataFrame, c104y: pd.DataFrame, c106y: pd.DataFrame) -> dict:
    # ROIC
    roic = mongo_utils.sum_of_row(c104q, 'ROIC')
    roic_dict = mongo_utils.extract_timeseries_from_c1034_df(c104y, 'ROIC')
    roic_eval = evaluate_roic(roic_dict)

    # ROE
    _, roe = mongo_utils.get_latest_valid_value(c104q, 'ROE')
    roe_data = mongo_utils.extract_timeseries_from_c1034_df(c104y, 'ROE')
    debt_ratio_data = mongo_utils.extract_timeseries_from_c1034_df(c104y, '부채비율')
    equity_data = mongo_utils.extract_timeseries_from_c1034_df(c104y, '자기자본증가율')
    roe_eval = evaluate_roe(roe_data, debt_ratio_data, equity_data)
    peer_roe = mongo_utils.extract_timeseries_from_c106_df(c106y, 'ROE(%)')

    # ROA
    _, roa = mongo_utils.get_latest_valid_value(c104q, 'ROA')
    roa_data = mongo_utils.extract_timeseries_from_c1034_df(c104y, 'ROA')
    try:
        asset_data = mongo_utils.extract_timeseries_from_c1034_df(c103재무상태표y, '자산총계')
    except ValueError:
        asset_data = mongo_utils.extract_timeseries_from_c1034_df(c103재무상태표y, '자산')

    roa_eval = evaluate_roa(roa_data, asset_data)

    return {
        "roic": {
            "r_value": roic,
            "evaluation": roic_eval,
            "timeseries": roic_dict,
        },
        "roe": {
            "r_value": roe,
            "evaluation": roe_eval,
            "timeseries": roe_data,
            "peer": peer_roe,
        },
        "roa": {
            "r_value": roa,
            "evaluation": roa_eval,
            "timeseries": roa_data,
        },
    }


def calc_FCF(c103현금흐름표y: pd.DataFrame, c103재무상태표y: pd.DataFrame) -> tuple[float, dict[str, float]]:
    """
    연도별 Free Cash Flow(FCF)를 계산하고 가장 최근 연도의 FCF 값과 시계열 전체를 반환합니다.

    반환값:
        (가장 최근 FCF 값, FCF 시계열 딕셔너리)
    """
    영업활동현금흐름_dict = mongo_utils.extract_timeseries_from_c1034_df(c103현금흐름표y, '영업활동으로인한현금흐름')
    if not 영업활동현금흐름_dict:
        return (float("nan"), {})

    try:
        capex_dict = mongo_utils.extract_timeseries_from_c1034_df(c103재무상태표y, '*CAPEX')
        mylogger.debug(f'CAPEX {capex_dict}')
    except ValueError:
        mylogger.warning("CAPEX가 없는 업종으로 영업현금흐름을 그대로 사용합니다.")
        sorted_fcf = dict(sorted(영업활동현금흐름_dict.items()))
        latest_value = list(sorted_fcf.values())[-1] if sorted_fcf else float("nan")
        return (latest_value, sorted_fcf)

    # FCF 계산
    fcf_dict = {
        date: round(value - capex_dict.get(date, 0), 2)
        for date, value in 영업활동현금흐름_dict.items()
    }

    sorted_fcf = dict(sorted(fcf_dict.items()))
    latest_value = list(sorted_fcf.values())[-1] if sorted_fcf else float("nan")

    mylogger.debug(f'fcf_dict {sorted_fcf}')
    return (latest_value, sorted_fcf)


def calc_PFCF(시가총액_억: float, fcf_dict: dict[str, float]) -> tuple[float, dict[str, float]]:
    """
    시가총액과 FCF 시계열을 기반으로 연도별 PFCF를 계산하고,
    가장 최근 값과 전체 시계열 딕셔너리를 반환합니다.

    반환값:
        (가장 최근 PFCF 값, 전체 PFCF 시계열 딕셔너리)
    """
    if math.isnan(시가총액_억) or not fcf_dict:
        mylogger.warning("시가총액 또는 FCF가 유효하지 않아 pFCF를 계산할 수 없습니다.")
        return (float("nan"), {})

    pfcf_dict = {
        date: round(시가총액_억 / fcf, 2) if fcf > 0 else math.nan
        for date, fcf in fcf_dict.items()
    }

    sorted_pfcf = dict(sorted(pfcf_dict.items()))
    latest_value = list(sorted_pfcf.values())[-1] if sorted_pfcf else float("nan")

    mylogger.debug(f'pfcf_dict : {sorted_pfcf}')
    return (latest_value, sorted_pfcf)


def evaluate_fcf(fcf_dict: dict[str, float]) -> dict:
    """
    FCF (Free Cash Flow) 시계열 데이터를 기반으로 점수화 및 등급 평가
    """
    values = [v for v in fcf_dict.values() if not math.isnan(v)]
    if not values:
        return {"평균": 0.0, "점수": 0, "등급": "N/A"}

    avg_fcf = sum(values) / len(values)
    score = math_utils.score_from_threshold(avg_fcf, [(1000, 30), (500, 25), (0, 15), (-100, 5)])
    grade = math_utils.grade_from_score(score, [(30, "A+ (탁월)"), (25, "A (우수)"), (15, "B (보통)"), (5, "C (불안정)"), (0, "D (위험)")])

    return {
        "평균": round(avg_fcf, 2),
        "점수": score,
        "등급": grade
    }


def evaluate_pfcf(pfcf_dict: dict[str, float]) -> dict:
    """
    PFCF (Price / Free Cash Flow) 시계열 데이터를 기반으로 점수화 및 등급 평가
    """
    values = [v for v in pfcf_dict.values() if not math.isnan(v) and v > 0]
    if not values:
        return {"평균": 0.0, "점수": 0, "등급": "N/A"}

    avg_pfcf = sum(values) / len(values)
    score = math_utils.score_from_threshold(avg_pfcf, [(0, 30), (5, 25), (10, 15), (15, 5)])
    grade = math_utils.grade_from_score(score, [(30, "A+ (매우 저평가)"), (25, "A (저평가)"), (15, "B (보통)"),
                                     (5, "C (고평가)"), (0, "D (매우 고평가)")])

    return {
        "평균": round(avg_pfcf, 2),
        "점수": score,
        "등급": grade
    }


def evaluate_pcr(pcr_data: dict[str, float]) -> dict:
    """
    PCR 시계열 데이터를 기반으로 점수화 및 등급 평가
    """
    if not pcr_data:
        return {
            "평균": 0.0,
            "변동성": 0.0,
            "추세": "없음",
            "점수": 0,
            "등급": "N/A"
        }

    sorted_data = sorted(pcr_data.items(), key=lambda x: _extract_year(x[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    avg_pcr = sum(values) / len(values)
    volatility = math_utils.calculate_volatility(values)
    trend = values[-1] - values[0]

    trend_text = "하락" if trend < 0 else "상승" if trend > 0 else "보합"

    # 점수 계산
    score = 0
    score += math_utils.score_from_threshold(avg_pcr, [(0, 30), (5, 25), (10, 15), (15, 5)])
    score += math_utils.score_from_threshold(1 / (volatility + 0.001), [(1 / 1, 20), (1 / 3, 10)])  # 변동성 작을수록 유리
    score += math_utils.score_from_threshold(-trend, [(1, 10), (0, 5)])  # 하락 추세 유리

    grade = math_utils.grade_from_score(score, [(50, "A+ (탁월)"), (35, "A (우수)"), (20, "B (보통)"),
                                     (10, "C (불안정)"), (0, "D (위험)")])

    return {
        "평균": round(avg_pcr, 2),
        "변동성": round(volatility, 2),
        "추세": trend_text,
        "점수": score,
        "등급": grade
    }


def calc_가치지표(c103현금흐름표y: pd.DataFrame, c103재무상태표y: pd.DataFrame, c104q: pd.DataFrame, 시가총액_억: float) -> dict:
    # FCF, PFCF, PCR 계산
    fcf, fcf_dict = calc_FCF(c103현금흐름표y, c103재무상태표y)
    pfcf, pfcf_dict = calc_PFCF(시가총액_억, fcf_dict)

    _, pcr = mongo_utils.get_latest_valid_value(c104q, "PCR")
    pcr_dict = mongo_utils.extract_timeseries_from_c1034_df(c104q, 'PCR')

    # 평가
    fcf_eval = evaluate_fcf(fcf_dict)
    pfcf_eval = evaluate_pfcf(pfcf_dict)
    pcr_eval = evaluate_pcr(pcr_dict)

    return {
        "fcf": {
            "r_value": fcf,
            "timeseries": fcf_dict,
            "evaluation": fcf_eval
        },
        "pfcf": {
            "r_value": pfcf,
            "timeseries": pfcf_dict,
            "evaluation": pfcf_eval
        },
        "pcr": {
            "r_value": pcr,
            "timeseries": pcr_dict,
            "evaluation": pcr_eval
        }
    }


def calc_유동비율(c103재무상태표q: pd.DataFrame, c103현금흐름표q: pd.DataFrame, c104q: pd.DataFrame) -> tuple[str, float]:
    유동비율date, 유동비율value = mongo_utils.get_latest_valid_value(c104q, "유동비율")
    mylogger.info(f'유동비율 raw : {유동비율value}/({유동비율date})')

    if math.isnan(유동비율value) or 유동비율value < 100:
        유동자산date, 유동자산value = calc_유동자산(c103재무상태표q)
        유동부채date, 유동부채value = calc_유동부채(c103재무상태표q)

        추정영업현금흐름value = mongo_utils.sum_of_row(c103현금흐름표q, '영업활동으로인한현금흐름')

        try:
            계산된유동비율 = round(((유동자산value + 추정영업현금흐름value) / 유동부채value) * 100, 2)
        except ZeroDivisionError:
            mylogger.info(f'유동자산: {유동자산value} + 추정영업현금흐름: {추정영업현금흐름value} / 유동부채: {유동부채value}')
            계산된유동비율 = float('inf')

        mylogger.debug(f'계산된 유동비율 : {계산된유동비율}')

        try:
            date, *_ = math_utils.date_set(유동자산date, 유동부채date)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''

        mylogger.warning(f'유동비율 이상(100 이하 또는 nan) : {유동비율value} -> 재계산 : {계산된유동비율}')
        return date, 계산된유동비율
    else:
        return 유동비율date, 유동비율value


def evaluate_inventory_efficiency(재고자산회전율: dict[str, float], 매출액증가율: dict[str, float]) -> dict:
    """
    재고자산회전률과 매출증가율 시계열 데이터를 바탕으로 종합 평가합니다.
    """

    # 시계열 정렬
    sorted_inv = sorted(재고자산회전율.items(), key=lambda x: _extract_year(x[0]))
    sorted_sales = sorted(매출액증가율.items(), key=lambda x: _extract_year(x[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_inv and math.isnan(sorted_inv[-1][1]):
        cleaned_inv = sorted_inv[:-1]
    else:
        cleaned_inv = sorted_inv
    inv_vals = [v for _, v in cleaned_inv]

    if sorted_sales and math.isnan(sorted_sales[-1][1]):
        cleaned_sales = sorted_sales[:-1]
    else:
        cleaned_sales = sorted_sales
    sales_vals = [v for _, v in cleaned_sales]

    if not inv_vals or not sales_vals:
        return {"평균 회전률": 0.0, "점수": 0, "등급": "N/A"}

    avg_turnover = sum(inv_vals) / len(inv_vals)
    volatility = math_utils.calculate_volatility(inv_vals)

    # 회전률 추세와 매출 추세
    turnover_trend = inv_vals[-1] - inv_vals[0]
    sales_trend = sales_vals[-1] - sales_vals[0]

    # 점수 계산
    score = 0

    # 평균 회전률 점수
    score += math_utils.score_from_threshold(avg_turnover, [(10, 40), (6, 30), (3, 15)])

    # 변동성 점수 (낮을수록 좋음)
    score += math_utils.score_from_threshold(-volatility, [(-1, 20), (-3, 10)])

    # 추세에 따른 조정
    if turnover_trend > 0 and sales_trend > 0:
        score += 20
    elif turnover_trend < 0 and sales_trend > 0:
        score -= 10
    elif turnover_trend > 0 and sales_trend < 0:
        score += 5
    elif turnover_trend < 0 and sales_trend < 0:
        score -= 5

    # 시계열 길이 보너스
    score += math_utils.score_from_threshold(len(inv_vals), [(5, 10), (3, 5)])

    grade = math_utils.grade_from_score(
        score, [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (보통)"), (30, "C (불안정)"), (0, "D (위험)")])

    return {
        "평균 회전률": round(avg_turnover, 2),
        "변동성": round(volatility, 2),
        "회전률 추세": "상승" if turnover_trend > 0 else "하락" if turnover_trend < 0 else "보합",
        "매출 추세": "상승" if sales_trend > 0 else "하락" if sales_trend < 0 else "보합",
        "점수": score,
        "등급": grade
    }


def evaluate_interest_coverage(이자보상배율: dict[str, float]) -> dict:
    """
    이자보상배율 시계열 데이터를 평가합니다.

    - 평균값이 높을수록 좋음
    - 변동성이 낮을수록 안정적임
    - 시계열 추세가 상승이면 긍정적으로 평가
    """

    # 시계열 정렬 (예: "2020/12", "2021/12" → 연도 기준 정렬)
    sorted_data = sorted(이자보상배율.items(), key=lambda x: int(x[0].split("/")[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    if not values:
        return {"평균 보상배율": 0.0, "점수": 0, "등급": "N/A"}

    avg_ratio = sum(values) / len(values)
    volatility = math_utils.calculate_volatility(values)
    trend = values[-1] - values[0]

    score = 0

    # 평균 보상배율 점수 (기준 예시)
    score += math_utils.score_from_threshold(avg_ratio, [(10, 40), (5, 30), (2, 15)])

    # 변동성 점수 (낮을수록 좋음)
    score += math_utils.score_from_threshold(-volatility, [(-0.5, 20), (-1.5, 10)])

    # 추세
    if trend > 0:
        score += 10
    elif trend < 0:
        score -= 10

    # 시계열 길이에 따른 보너스
    score += math_utils.score_from_threshold(len(values), [(5, 10), (3, 5)])

    grade = math_utils.grade_from_score(
        score,
        [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (보통)"), (30, "C (불안정)"), (0, "D (위험)")]
    )

    return {
        "평균 보상배율": round(avg_ratio, 2),
        "변동성": round(volatility, 2),
        "추세": "상승" if trend > 0 else "하락" if trend < 0 else "보합",
        "점수": score,
        "등급": grade
    }


def evaluate_nwc_turnover(순운전자본회전율: dict[str, float]) -> dict:
    """
    순운전자본회전율 시계열 데이터를 바탕으로 평가합니다.

    - 높은 값: 자본 효율성 양호
    - 낮은 값: 비효율적 운용 가능성
    - 변동성 낮고, 상승 추세면 긍정적 평가
    """

    # 연도 정렬
    sorted_data = sorted(순운전자본회전율.items(), key=lambda x: int(x[0].split("/")[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    if not values:
        return {"평균 회전율": 0.0, "점수": 0, "등급": "N/A"}

    avg = sum(values) / len(values)
    volatility = math_utils.calculate_volatility(values)
    trend = values[-1] - values[0]

    score = 0

    # 평균 회전율 평가
    score += math_utils.score_from_threshold(avg, [(5, 40), (3, 30), (1, 15)])

    # 변동성 점수 (낮을수록 좋음)
    score += math_utils.score_from_threshold(-volatility, [(-0.5, 20), (-1.5, 10)])

    # 추세 반영
    if trend > 0:
        score += 10
    elif trend < 0:
        score -= 10

    # 시계열 길이 보너스
    score += math_utils.score_from_threshold(len(values), [(5, 10), (3, 5)])

    # 등급 변환
    grade = math_utils.grade_from_score(
        score,
        [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (보통)"), (30, "C (불안정)"), (0, "D (위험)")]
    )

    return {
        "평균 회전율": round(avg, 2),
        "변동성": round(volatility, 2),
        "추세": "상승" if trend > 0 else "하락" if trend < 0 else "보합",
        "점수": score,
        "등급": grade
    }


def evaluate_net_debt_ratio(순부채비율: dict[str, float]) -> dict:
    """
    순부채비율(Net Debt Ratio) 시계열 데이터를 바탕으로 평가합니다.

    - 낮을수록 좋음 (0 이하: 순현금 상태)
    - 변동성 낮고 하락 추세면 우수
    """

    # 시계열 정렬
    sorted_data = sorted(순부채비율.items(), key=lambda x: int(x[0].split("/")[0]))

    # 마지막 값만 nan일 경우 제외
    if sorted_data and math.isnan(sorted_data[-1][1]):
        cleaned_data = sorted_data[:-1]
    else:
        cleaned_data = sorted_data

    values = [v for _, v in cleaned_data]

    if not values:
        return {"평균 순부채비율": 0.0, "점수": 0, "등급": "N/A"}

    avg = sum(values) / len(values)
    volatility = math_utils.calculate_volatility(values)
    trend = values[-1] - values[0]

    score = 0

    # 평균 순부채비율 점수 (낮을수록 좋음)
    score += math_utils.score_from_threshold(-avg, [(-100, 40), (-50, 30), (-10, 15)])

    # 변동성 점수 (낮을수록 좋음)
    score += math_utils.score_from_threshold(-volatility, [(-10, 20), (-30, 10)])

    # 추세 점수 (감소하면 좋음)
    if trend < 0:
        score += 10
    elif trend > 0:
        score -= 10

    # 시계열 길이 보너스
    score += math_utils.score_from_threshold(len(values), [(5, 10), (3, 5)])

    # 등급 계산
    grade = math_utils.grade_from_score(
        score,
        [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (보통)"), (30, "C (주의 필요)"), (0, "D (위험)")]
    )

    return {
        "평균 순부채비율": round(avg, 2),
        "변동성": round(volatility, 2),
        "추세": "하락" if trend < 0 else "상승" if trend > 0 else "보합",
        "점수": score,
        "등급": grade
    }


def evaluate_growth_profitability(매출증가율_시계열: dict[str, float], 영업이익률_업종비교: dict[str, float]) -> dict:
    """
    매출액 증가율 시계열과 경쟁사 영업이익률을 활용한 성장성/수익성 평가
    """


    # 1. 시계열 정렬 및 유효 값 필터링
    sorted_sales = sorted(매출증가율_시계열.items(), key=lambda x: int(x[0].split("/")[0]))
    sales_values = [v for _, v in sorted_sales if not math.isnan(v)]

    if not sales_values:
        return {"점수": 0, "등급": "N/A"}

    # 2. 지표 계산
    sales_avg = sum(sales_values) / len(sales_values)
    sales_volatility = math_utils.calculate_volatility(sales_values)
    sales_trend = sales_values[-1] - sales_values[0] if len(sales_values) > 1 else 0

    # 3. 영업이익률 우위 계산
    try:
        기업명, 대상_이익률 = list(영업이익률_업종비교.items())[0]
        경쟁사_이익률 = [v for i, v in enumerate(영업이익률_업종비교.values()) if i != 0 and not math.isnan(v)]
        경쟁사_평균 = sum(경쟁사_이익률) / len(경쟁사_이익률) if 경쟁사_이익률 else 0
        수익성_우위 = 대상_이익률 - 경쟁사_평균
        mylogger.debug(f'대상_이익률({대상_이익률}) - 경쟁사_평균({경쟁사_평균}) = 수익성우위({수익성_우위})')
    except IndexError:
        mylogger.warning("영업이익률_업종비교 자료가 없습니다.")
        기업명 = ''
        수익성_우위 = 0.0

    # 4. 점수 계산
    score = 0

    # 평균 매출 증가율
    score += math_utils.score_from_threshold(sales_avg, [(10, 40), (5, 30), (0, 15)])

    # 매출 추세
    if sales_trend > 0:
        score += 10
    elif sales_trend < 0:
        score -= 10

    # 영업이익률 우위
    score += math_utils.score_from_threshold(수익성_우위, [(5, 30), (0, 20), (-5, 10)])
    if 수익성_우위 < -5:
        score -= 10

    # 시계열 길이 안정성
    score += math_utils.score_from_threshold(len(sales_values), [(5, 10), (3, 5)])

    # 5. 등급 산정
    grade = math_utils.grade_from_score(
        score, [(80, "A+ (탁월)"), (65, "A (우수)"), (50, "B (양호)"), (30, "C (보통)"), (0, "D (위험)")]
    )

    return {
        "기업명": 기업명,
        "매출 증가율 평균": round(sales_avg, 2),
        "매출 변동성": round(sales_volatility, 2),
        "매출 추세": "상승" if sales_trend > 0 else "하락" if sales_trend < 0 else "보합",
        "영업이익률 우위": round(수익성_우위, 2),
        "점수": score,
        "등급": grade
    }
