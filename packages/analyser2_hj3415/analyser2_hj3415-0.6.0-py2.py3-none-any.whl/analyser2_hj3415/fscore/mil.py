from db2_hj3415.valuation import MilData, Evaluation
from motor.motor_asyncio import AsyncIOMotorClient

from analyser2_hj3415.fscore.utils import mongo_utils, financial
from db2_hj3415.nfs import C101, c101, c106

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')

def build_mil평가결과(raw: dict) -> Evaluation:
    return Evaluation(
        최근값=raw.get('r_value'),
        시계열=raw.get('timeseries'),
        평가결과=raw.get('evaluation'),
    )

async def generate_data(code: str) -> MilData:
    c101_data: C101 = await c101.get_latest(code)
    if c101_data is None:
        raise ValueError(f"{code}에 해당하는 c101 데이터가 없습니다.")
    종목명 = c101_data.종목명
    시가총액_억 = mongo_utils.get_marketcap_billion(c101_data)
    mylogger.debug(f"시가총액(억) : {시가총액_억}")
    mylogger.info(f"{code}/{종목명}의 MilData를 생성합니다.")

    # C103, C104, C106 데이터
    c103_data = await mongo_utils.prepare_c1034_data('c103', code)
    c104_data = await mongo_utils.prepare_c1034_data('c104', code)
    c106_data = await c106.get_latest(code, as_type='dataframe')

    재무상태표q_df = c103_data['재무상태표q']
    손익계산서q_df = c103_data['손익계산서q']
    현금흐름표q_df = c103_data['현금흐름표q']
    재무상태표y_df = c103_data['재무상태표y']
    현금흐름표y_df = c103_data['현금흐름표y']
    c104q_df, c104y_df = c104_data['q'], c104_data['y']
    c106y_df = c106_data['y']

    # 계산
    _, 당기순이익 = financial.calc_당기순이익(재무상태표q_df, 손익계산서q_df, 재무상태표y_df)
    주주수익률 = financial.calc_주주수익률(현금흐름표q_df, 시가총액_억)
    이익지표 = financial.calc_이익지표(현금흐름표q_df, 시가총액_억, 당기순이익)
    투자수익률 = financial.calc_투자수익률(재무상태표y_df, c104q_df, c104y_df, c106y_df)
    가치지표 = financial.calc_가치지표(현금흐름표y_df, 재무상태표y_df, c104q_df, 시가총액_억)

    # Mil평가결과 생성
    roic_data = build_mil평가결과(투자수익률.get('roic', {}))
    roe_data = build_mil평가결과(투자수익률.get('roe', {}))
    roa_data = build_mil평가결과(투자수익률.get('roa', {}))
    fcf_data = build_mil평가결과(가치지표.get('fcf', {}))
    pfcf_data = build_mil평가결과(가치지표.get('pfcf', {}))
    pcr_data = build_mil평가결과(가치지표.get('pcr', {}))

    return MilData(
        코드=code,
        종목명=종목명,
        주주수익률=주주수익률,
        이익지표=이익지표,
        ROIC=roic_data,
        ROE=roe_data,
        ROA=roa_data,
        FCF=fcf_data,
        PFCF=pfcf_data,
        PCR=pcr_data,
    )









def get(refresh = False) -> MilData:
    """
    MilData 객체를 Redis 캐시에서 가져오거나 새로 생성하여 반환합니다.

    캐시에서 데이터를 검색하고, 없을 경우 `_generate_data`를 호출하여 데이터를 생성합니다.
    생성된 데이터는 Redis 캐시에 저장되어 재사용됩니다.

    매개변수:
        refresh (bool): 캐시를 무시하고 새로 데이터를 계산할지 여부. 기본값은 False.
        verbose (bool): 실행 중 상세 정보를 출력할지 여부. 기본값은 True.

    반환값:
        MilData: Redis 캐시에서 가져오거나 새로 생성된 MilData 객체.

    로그:
        - 캐시 검색 상태와 새로 생성된 데이터를 출력합니다.
    """
    redis_name = f"{self.code}_{self.REDIS_MIL_DATA_SUFFIX}"
    mylogger.debug(f"{self} redisname: '{redis_name}' / refresh : {refresh}")

    def fetch_generate_data(refresh_in: bool) -> dict:
        return self._generate_data(refresh_in) # type: ignore

    return myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh)

def bulk_get_data(codes: list[str], refresh: bool) -> dict[str, MilData]:
    return myredis.Corps.bulk_get_or_compute(
        [f"{code}_{cls.REDIS_MIL_DATA_SUFFIX}" for code in codes],
        lambda key: cls(key[:6])._generate_data(refresh=True),
        refresh=refresh
    )
