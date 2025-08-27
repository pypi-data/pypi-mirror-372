from typing import Callable

import pandas as pd
from db2_hj3415.valuation import BlueData, Evaluation
from db2_hj3415.nfs import C101, c101

from analyser2_hj3415.fscore.utils import financial, mongo_utils, math_utils

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


def make_evaluation(field: str, df_q: pd.DataFrame, df_y: pd.DataFrame, eval_func: Callable, *eval_args) -> tuple[str, Evaluation]:
    """공통 평가 데이터 생성 유틸 함수"""
    latest_date, latest_value = mongo_utils.get_latest_valid_value(df_q, field)
    timeseries = mongo_utils.extract_timeseries_from_c1034_df(df_y, field)
    evaluation_result = eval_func(timeseries, *eval_args)
    return latest_date, Evaluation(
        최근값=latest_value,
        시계열=timeseries,
        평가결과=evaluation_result,
    )


async def generate_data(code: str) -> BlueData:
    c101_data: C101 = await c101.get_latest(code)
    if c101_data is None:
        raise ValueError(f"{code}에 해당하는 c101 데이터가 없습니다.")
    종목명 = c101_data.종목명
    mylogger.info(f"{code}/{종목명}의 BlueData를 생성합니다.")

    # C103, C104 데이터
    c103_data = await mongo_utils.prepare_c1034_data('c103', code)
    c104_data = await mongo_utils.prepare_c1034_data('c104', code)

    재무상태표q_df = c103_data['재무상태표q']
    현금흐름표q_df = c103_data['현금흐름표q']
    c104q_df, c104y_df = c104_data['q'], c104_data['y']

    # 유동비율은 별도 계산
    d1, 유동비율 = financial.calc_유동비율(재무상태표q_df, 현금흐름표q_df, c104q_df)
    mylogger.info(f"유동비율 {유동비율} / [{d1}]")

    # 공통 지표 계산
    d2, 재고자산회전율_data = make_evaluation("재고자산회전율", c104q_df, c104y_df, financial.evaluate_inventory_efficiency,
                                            mongo_utils.extract_timeseries_from_c1034_df(c104y_df, "매출액증가율"))
    d3, 이자보상배율_data = make_evaluation("이자보상배율", c104q_df, c104y_df, financial.evaluate_interest_coverage)
    try:
        d4, 순운전자본회전율_data = make_evaluation("순운전자본회전율", c104q_df, c104y_df, financial.evaluate_nwc_turnover)
    except ValueError as e:
        mylogger.warning(f'{code}/{종목명} : {e} - 금융업종일 가능성')
        d4, 순운전자본회전율_data = '', None

    d5, 순부채비율_data = make_evaluation("순부채비율", c104q_df, c104y_df, financial.evaluate_net_debt_ratio)

    try:
        date_list = math_utils.date_set(d1, d2, d3, d4)
    except ValueError:
        mylogger.warning(f"유효한 날짜 없음: {[d1, d2, d3, d4]}")
        date_list = ['']

    return BlueData(
        코드=code,
        종목명=종목명,
        유동비율=유동비율,
        재고자산회전율=재고자산회전율_data,
        이자보상배율=이자보상배율_data,
        순운전자본회전율=순운전자본회전율_data,
        순부채비율=순부채비율_data,
        자료제출일=date_list,
    )






def get(self, refresh=False) -> BlueData:
    """
    BlueData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

    캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
    생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

    매개변수:
        refresh (bool): 캐시를 무시하고 새로 데이터를 계산할지 여부. 기본값은 False.
        verbose (bool): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

    반환값:
        BlueData: Redis 캐시에서 가져오거나 새로 생성된 BlueData 객체.

    로그:
        - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
    """
    redis_name = f"{self.code}_blue"
    mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

    def fetch_generate_data(refresh_in: bool) -> dict:
        return self._generate_data(refresh_in)  # type: ignore

    return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)
