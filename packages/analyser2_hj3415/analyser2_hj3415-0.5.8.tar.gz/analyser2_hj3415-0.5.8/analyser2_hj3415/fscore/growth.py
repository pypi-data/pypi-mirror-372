from motor.motor_asyncio import AsyncIOMotorClient

from db2_hj3415.valuation import GrowthData, Evaluation
from db2_hj3415.nfs import C101, c101, c106
from analyser2_hj3415.fscore.utils import financial, mongo_utils

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


async def generate_data(code: str) -> GrowthData:
    c101_data: C101 = await c101.get_latest(code)
    if c101_data is None:
        raise ValueError(f"{code}에 해당하는 c101 데이터가 없습니다.")
    종목명 = c101_data.종목명
    mylogger.info(f"{code}/{종목명}의 GrowthData를 생성합니다.")

    # C104, C106 데이터
    c104_data = await mongo_utils.prepare_c1034_data('c104', code)
    c106_data = await c106.get_latest(code, as_type='dataframe')

    c104q_df, c104y_df = c104_data['q'], c104_data['y']
    c106y_df = c106_data['y']

    _, 매출액증가율_r = mongo_utils.get_latest_valid_value(c104q_df, '매출액증가율')
    매출액증가율_dict = mongo_utils.extract_timeseries_from_c1034_df(c104y_df, '매출액증가율')

    mylogger.info(f'매출액증가율 : {매출액증가율_r} {매출액증가율_dict}')

    영업이익률_업종비교 = mongo_utils.extract_timeseries_from_c106_df(c106y_df, '영업이익률(%)')

    mylogger.info(f'영업이익률 업종비교 :  {영업이익률_업종비교}')

    평가결과 = financial.evaluate_growth_profitability(매출액증가율_dict, 영업이익률_업종비교)

    mylogger.info(f'평가결과 :  {평가결과}')

    return GrowthData(
        코드=code,
        종목명=종목명,
        매출액증가율=Evaluation(
            최근값=매출액증가율_r,
            시계열=매출액증가율_dict,
            평가결과=평가결과,
            영업이익률_업종비교=영업이익률_업종비교,
        )
    )


def get(self, refresh = False) -> GrowthData:
    """
    GrowthData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

    캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
    생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

    매개변수:
        refresh (bool, optional): 캐시 데이터를 무시하고 새로 계산할지 여부. 기본값은 False.
        verbose (bool, optional): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

    반환값:
        GrowthData: Redis 캐시에서 가져오거나 새로 생성된 GrowthData 객체.

    로그:
        - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
    """

    redis_name = f"{self.code}_growth"
    mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

    def fetch_generate_data(refresh_in: bool) -> dict:
        return self._generate_data(refresh_in) # type: ignore

    return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)