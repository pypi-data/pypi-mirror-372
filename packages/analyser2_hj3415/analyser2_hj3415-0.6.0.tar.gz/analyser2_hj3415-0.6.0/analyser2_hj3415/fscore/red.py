from collections import OrderedDict
import math

import pandas as pd
from db2_hj3415.valuation import RedData
from db2_hj3415.nfs import c101, C101
from analyser2_hj3415.fscore.utils import mongo_utils, financial, math_utils
from motor.motor_asyncio import AsyncIOMotorClient


from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


async def generate_data(code: str, expect_earn: float = 0.06) -> RedData:
    c101_data: C101 = await c101.get_latest(code)
    if c101_data is None:
        raise ValueError(f"{code}에 해당하는 c101 데이터가 없습니다.")
    종목명 = c101_data.종목명
    최근주가 = c101_data.주가
    발행주식 = c101_data.발행주식

    mylogger.info(f"{code}/{종목명}의 RedData를 생성합니다.")

    c103_data: dict[str, pd.DataFrame] = await mongo_utils.prepare_c1034_data('c103', code)
    재무상태표q_df = c103_data['재무상태표q']
    손익계산서q_df = c103_data['손익계산서q']
    재무상태표y_df = c103_data['재무상태표y']

    d1, 순이익 = financial.calc_당기순이익(재무상태표q_df, 손익계산서q_df, 재무상태표y_df)
    d2, 유동자산 = financial.calc_유동자산(재무상태표q_df)
    d3, 유동부채 = financial.calc_유동부채(재무상태표q_df)
    d4, 부채평가 = financial.calc_비유동부채(재무상태표q_df)

    d5, 투자자산 = mongo_utils.get_latest_valid_value(재무상태표q_df,'투자자산')
    d6, 투자부동산 = mongo_utils.get_latest_valid_value(재무상태표q_df,'투자부동산')
    _, 발행주식수 = mongo_utils.get_latest_valid_value(재무상태표q_df, '발행주식수')

    # 사업가치 계산: 순이익과 기대수익률 중 NaN 아닌 값만으로 계산
    if pd.notna(순이익) and pd.notna(expect_earn) and expect_earn != 0:
        사업가치 = round(순이익 / expect_earn, 1)
    else:
        사업가치 = math.nan

    # 재산가치 계산: NaN 항목은 제외하고 계산
    유동자산_ = 유동자산 if pd.notna(유동자산) else 0.0
    유동부채_ = 유동부채 if pd.notna(유동부채) else 0.0
    투자자산_ = 투자자산 if pd.notna(투자자산) else 0.0
    투자부동산_ = 투자부동산 if pd.notna(투자부동산) else 0.0

    재산가치 = round(유동자산_ - (유동부채_ * 1.2) + 투자자산_ + 투자부동산_, 1)

    if math.isnan(발행주식수):
        발행주식수 = 발행주식
    else:
        발행주식수 = 발행주식수 * 1000

    if any(pd.isna(x) for x in [사업가치, 재산가치, 부채평가, 발행주식수]) or 발행주식수 == 0:
        red_price = math.nan
    else:
        red_price = round(((사업가치 + 재산가치 - 부채평가) * 1e8) / 발행주식수)

    score = math_utils.calc_score(최근주가, red_price)

    try:
        date_list = math_utils.date_set(d1, d2, d3, d4)
    except ValueError:
        mylogger.warning(f"유효한 날짜 없음: {[d1, d2, d3, d4]}")
        date_list = ['']
        
    data = {
        "코드": code,
        "종목명": 종목명,
        
        "사업가치": 사업가치,
        "지배주주당기순이익": 순이익,
        "expect_earn": expect_earn,

        "재산가치": 재산가치,
        "유동자산": 유동자산,
        "유동부채": 유동부채,
        "투자자산": 투자자산,
        "투자부동산": 투자부동산,

        "부채평가": 부채평가,
        "발행주식수": 발행주식수,

        "자료제출일": date_list,
        "주가": 최근주가,
        "red_price": red_price,
        
        "score": score
    }

    return RedData(**data)







def get_red_data(code: str, expect_earn: float = 0.06, refresh: bool = False) -> RedData:
    redis_name = f"{code}_{REDIS_RED_DATA_SUFFIX}_{expect_earn}"
    return myredis.Base.fetch_and_cache_data(
        redis_name,
        refresh,
        lambda _: generate_data(code, expect_earn, refresh=True),
        refresh
    )

def bulk_get_red_data(codes: list[str], expect_earn: float = 0.06, refresh: bool = False) -> dict[str, RedData]:
    return myredis.Corps.bulk_get_or_compute(
        [f"{code}_{REDIS_RED_DATA_SUFFIX}_{expect_earn}" for code in codes],
        lambda key: generate_data(key[:6], expect_earn, refresh=True),
        refresh=refresh
    )

def red_ranking(expect_earn: float = 0.06, refresh: bool = False) -> OrderedDict[str, RedData]:
    mylogger.info("**** Start red ranking ... ****")
    codes = myredis.Corps.list_all_codes()
    data = bulk_get_red_data(codes, expect_earn, refresh)
    return OrderedDict(sorted(data.items(), key=lambda x: x[1].score, reverse=True))