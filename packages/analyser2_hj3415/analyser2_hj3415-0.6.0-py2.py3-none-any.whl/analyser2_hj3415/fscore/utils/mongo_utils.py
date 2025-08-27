from typing import Literal

import pandas as pd
import numpy as np
from db2_hj3415.nfs import c103, C101, c104
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


async def prepare_c1034_data(col: Literal['c103','c104'], code: str) -> dict[str, pd.DataFrame]:
    match col:
        case 'c103':
            data = await c103.get_latest(code, as_type='dataframe')
        case 'c104':
            data = await c104.get_latest(code, as_type='dataframe')
        case _:
            raise ValueError(f"{col} - 잘못된 컬렉션명")

    if data is None:
        raise ValueError(f"{code}에 해당하는 {col} 데이터가 없습니다.")

    cols_to_remove = ['전분기대비', '전분기대비 1', '전년대비', '전년대비 1']
    for df in data.values():
        df.drop(columns=cols_to_remove, errors='ignore', inplace=True)

    mylogger.debug(f"{col} - {code} 데이터 컬럼 정리 완료: {list(data.keys())}")
    return data


def sum_of_row(df: pd.DataFrame, row_name: str) -> float | None:
    # 해당 항목 이름의 행들을 모두 선택
    target_rows = df[df['항목'] == row_name]

    if target_rows.empty:
        mylogger.warning(f"항목 '{row_name}'이(가) 존재하지 않습니다.")
        return None

    # 연도/분기 형식의 열만 선택
    year_cols = [col for col in df.columns if '/' in col]

    result: list[float] = []
    for _, row in target_rows.iterrows():
        values = row[year_cols]
        if values.isna().all():
            result.append(np.nan)
        else:
            result.append(round(values.sum(skipna=True), 1))

    def first_non_nan(values: list[float]) -> float:
        return next((v for v in values if not np.isnan(v)), np.nan)

    return first_non_nan(result)


def get_latest_valid_value(df: pd.DataFrame, row_name: str) -> tuple[str, float]:
    """
    특정 항목의 가장 최근 유효한 값과 해당 열 이름(연도/분기)을 반환합니다.
    최대 2개의 셀만 확인합니다.

    Args:
        df (pd.DataFrame): 데이터프레임
        row_name (str): '항목' 열에서 찾을 항목 이름

    Returns:
        tuple[str, float] | None: (열 이름, 값) 튜플. 전부 NaN이면 None
    """
    row = df[df['항목'] == row_name]
    if row.empty:
        mylogger.warning(f"'{row_name}' 항목이 존재하지 않습니다.")
        return '', np.nan

    time_cols = sorted(
        [col for col in df.columns if '/' in col or col.endswith('/12')],
        reverse=True
    )

    attempts = 0
    for col in time_cols:
        if attempts >= 2:
            break  # 2회 이상 시도 금지
        val = row[col].values[0]
        attempts += 1
        if pd.notna(val):
            return col, float(val)

    return '', np.nan  # 최대 2번 시도 후에도 유효값을 못 찾은 경우


def extract_row_name(df: pd.DataFrame) -> list[str]:
    """
    DataFrame에서 '항목' 컬럼의 고유값 리스트를 반환합니다.

    Args:
        df (pd.DataFrame): 대상 데이터프레임

    Returns:
        list[str]: '항목' 열의 중복 제거된 고유 항목 리스트
    """
    if '항목' not in df.columns:
        raise ValueError("'항목' 컬럼이 존재하지 않습니다.")

    return df['항목'].dropna().unique().tolist()


def extract_timeseries_from_c1034_df(df: pd.DataFrame, 항목명: str) -> dict[str, float]:
    """
    지정한 항목의 시계열 데이터를 딕셔너리로 추출합니다.

    매개변수:
        df (pd.DataFrame): 항목별 시계열 지표가 담긴 데이터프레임
        항목명 (str): 추출하고자 하는 항목 이름 (예: 'ROIC')

    반환값:
        dict[str, float]: 연도(컬럼명)를 key, 수치를 value로 하는 딕셔너리
    """
    filtered = df[df['항목'] == 항목명]
    if filtered.empty:
        mylogger.warning(f"[경고] 항목 '{항목명}' 없음 → 빈 dict 반환됨")
        return {}

    row = filtered.iloc[0]
    time_series = row.drop(labels=['항목', '분류', '전분기대비', '전분기대비 1', '전년대비', '전년대비 1'], errors='ignore').to_dict()
    return {str(k): float(v) for k, v in time_series.items() if v is not None}


def extract_timeseries_from_c106_df(df: pd.DataFrame, 항목명: str) -> dict[str, float]:
    try:
        if not df.empty:
            mylogger.debug(df)
            row = df[df['항목2'] == 항목명].iloc[0]
            mylogger.debug(row)
            # '항목'과 '전년대비' 컬럼 제외
            time_series = row.drop(labels=['항목', '항목2'],
                                   errors='ignore').to_dict()
            return {
                str(k): float(v)
                for k, v in time_series.items()
                if v is not None
            }
        else:
            return {}
    except IndexError:
        raise ValueError(f"항목 '{항목명}'을(를) 찾을 수 없습니다.")


def get_marketcap_billion(c101_data: C101) -> float:
    """
    기업의 시가총액(억 단위)을 반환합니다.

    매개변수:
        c101_data (dict): 기업의 c101 데이터.

    반환값:
        float: 시가총액(억 단위). 유효하지 않으면 np.nan 반환.
    """
    raw_value = c101_data.시가총액
    try:
        market_cap = float(raw_value) / 100_000_000
        return round(market_cap, 2)
    except (TypeError, ValueError):
        return np.nan

