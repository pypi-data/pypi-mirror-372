from collections import OrderedDict
import datetime
from typing import Tuple, List, Dict, Union
import time

import yfinance as yf
import pandas as pd
from prophet import Prophet
from sklearn.preprocessing import StandardScaler

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser import eval, MIs, tsa
from analyser_hj3415.analyser.tsa.common import ProphetChartData, ProphetLatestData


mylogger = setup_logger(__name__,'WARNING')


class MyProphet:

    REDIS_LATEST_DATA_SUFFIX = "myprophet_data"

    def __init__(self, ticker: str):
        mylogger.debug(f'set up ticker : {ticker}')
        self.scaler = StandardScaler()
        self.model = Prophet()
        self._ticker = ticker
        self.initialized = False

        self.raw_data = pd.DataFrame()
        self.df_real = pd.DataFrame()
        self.df_forecast = pd.DataFrame()

    @property
    def ticker(self) -> str:
        """
        현재 설정된 티커를 반환합니다.

        반환값:
            str: 현재 티커 값.
        """
        return self._ticker

    @ticker.setter
    def ticker(self, ticker: str):
        """
        티커 값을 변경하고 관련 데이터를 초기화합니다.

        매개변수:
            ticker (str): 새로 설정할 티커 값.
        """
        mylogger.debug(f'change ticker : {self.ticker} -> {ticker}')
        self.scaler = StandardScaler()
        self.model = Prophet()
        self._ticker = ticker
        self.initialized = False

        self.raw_data = pd.DataFrame()
        self.df_real = pd.DataFrame()
        self.df_forecast = pd.DataFrame()

    def initializing(self):
        """
        Prophet 모델 사용을 위한 데이터를 초기화합니다.

        - Yahoo Finance에서 데이터를 가져옵니다.
        - 데이터를 Prophet 형식에 맞게 전처리합니다.
        - Prophet 모델을 사용하여 예측 데이터를 생성합니다.
        """
        def get_raw_data(max_retries: int = 3, delay_sec: int = 2) -> pd.DataFrame:
            """
            Yahoo Finance에서 4년간의 주가 데이터를 가져옵니다.

            반환값:
                pd.DataFrame: 가져온 주가 데이터프레임.
            """
            # 오늘 날짜 가져오기
            today = datetime.datetime.today()

            # 4년 전 날짜 계산 (4년 = 365일 * 4)
            four_years_ago = today - datetime.timedelta(days=365 * 4)

            # 시도 횟수만큼 반복
            for attempt in range(1, max_retries + 1):
                try:
                    data = yf.download(
                        tickers=self.ticker,
                        start=four_years_ago.strftime('%Y-%m-%d'),
                        # end=today.strftime('%Y-%m-%d') 가장 최근날짜까지 조회위해 비활성 처리
                    )
                    # 데이터가 비어있지 않다면 성공으로 판단
                    if not data.empty:
                        return data
                    else:
                        # 다운로드 자체는 성공했지만, 빈 데이터가 반환될 경우
                        print(f"[{attempt}/{max_retries}] {self.ticker} 다운로드 결과가 비어 있습니다. 재시도합니다...")
                except Exception as e:
                    # 예외 발생 시, 재시도
                    print(f"[{attempt}/{max_retries}] {self.ticker} 다운로드 실패: {e}. 재시도합니다...")

                # 재시도 전 대기
                time.sleep(delay_sec)

            mylogger.error(f"{self.ticker} 주가 데이터를 다운로드하지 못했습니다 (최대 {max_retries}회 시도 실패).")
            return pd.DataFrame()

        def preprocessing_for_prophet() -> pd.DataFrame:
            """
            Prophet 모델에서 사용할 수 있도록 데이터를 준비합니다.

            - 'Close'와 'Volume' 열을 사용.
            - 날짜를 'ds', 종가를 'y', 거래량을 'volume'으로 변경.
            - 거래량 데이터를 정규화하여 'volume_scaled' 열 추가.

            반환값:
                pd.DataFrame: Prophet 모델 입력 형식에 맞게 처리된 데이터프레임.
            """
            df = self.raw_data[['Close', 'Volume']].reset_index()
            df.columns = ['ds', 'y', 'volume']  # Prophet의 형식에 맞게 열 이름 변경

            # ds 열에서 타임존 제거
            df['ds'] = df['ds'].dt.tz_localize(None)
            # 추가 변수를 정규화
            df['volume_scaled'] = self.scaler.fit_transform(df[['volume']])

            mylogger.debug('_preprocessing_for_prophet')
            mylogger.debug(df)
            self.initialized = True
            return df

        def make_forecast() -> pd.DataFrame:
            """
            Prophet 모델을 사용하여 향후 180일간 주가를 예측합니다.

            - 거래량 데이터('volume_scaled')를 추가 변수로 사용.
            - 예측 결과를 데이터프레임으로 반환.

            반환값:
                pd.DataFrame: 예측 결과를 포함한 데이터프레임.
            """
            # 정규화된 'volume_scaled' 변수를 외부 변수로 추가
            self.model.add_regressor('volume_scaled')

            self.model.fit(self.df_real)

            # 향후 180일 동안의 주가 예측
            future = self.model.make_future_dataframe(periods=180)
            mylogger.debug('_make_forecast_future')
            mylogger.debug(future)

            # 미래 데이터에 거래량 추가 (평균 거래량을 사용해 정규화)
            future_volume = pd.DataFrame({'volume': [self.raw_data['Volume'].mean()] * len(future)})
            future['volume_scaled'] = self.scaler.transform(future_volume[['volume']])

            forecast = self.model.predict(future)
            mylogger.debug('_make_forecast')
            mylogger.debug(forecast)
            return forecast

        mylogger.debug(f"{self.ticker} : Initializing data for MyProphet")

        self.scaler = StandardScaler()
        self.model = Prophet()

        self.raw_data = get_raw_data()
        mylogger.debug(self.raw_data)
        try:
            self.df_real = preprocessing_for_prophet()
            self.df_forecast = make_forecast()
        except (ValueError, KeyError) as e:
            mylogger.error(f"{self.ticker} : 빈 데이터프레임...{e}")
            self.df_real = pd.DataFrame()
            self.df_forecast = pd.DataFrame()

    def _make_prophet_latest_data(self) -> ProphetLatestData:
        def scoring(price: float, yhat_lower: float, yhat_upper: float, method: str = 'sigmoid') -> Tuple[str, int]:
            """
            주어진 가격과 임계값을 기준으로 매매 행동('buy', 'sell', 'hold')과 점수를 결정합니다.

            매개변수:
                price (float): 자산의 현재 가격.
                yhat_lower (float): 가격 예측의 하한 임계값.
                yhat_upper (float): 가격 예측의 상한 임계값.
                method (str, optional): 점수를 계산하는 방법 ('sigmoid' 또는 'log'). 기본값은 'sigmoid'.

            반환값:
                Tuple[str, int]: 매매 행동('buy', 'sell', 'hold')과 관련 점수로 이루어진 튜플.

            예외:
                ValueError: 지원되지 않는 점수 계산 방법이 제공된 경우 발생.
            """

            def calculate_score(deviation: float, method_in: str) -> int:
                if method_in == 'sigmoid':
                    return tools.to_int(eval.Tools.sigmoid_score(deviation))
                elif method_in == 'log':
                    return tools.to_int(eval.Tools.log_score(deviation))
                else:
                    raise ValueError(f"Unsupported scoring method: {method}")

            buying_deviation = eval.Tools.cal_deviation(price, yhat_lower)
            buying_score = calculate_score(buying_deviation, method)
            if price >= yhat_lower:
                buying_score = -buying_score

            selling_deviation = eval.Tools.cal_deviation(price, yhat_upper)
            selling_score = calculate_score(selling_deviation, method)
            if price <= yhat_upper:
                selling_score = -selling_score

            if buying_score > 0:
                return 'buy', buying_score
            elif selling_score > 0:
                return 'sell', selling_score
            else:
                return 'hold', 0

        if not self.initialized:
            self.initializing()
        mylogger.info(f'{self.ticker} _make_prophet_latest_data')
        try:
            latest_row = self.df_real.iloc[-1]
            latest_yhat = \
                self.df_forecast.loc[
                    self.df_forecast['ds'] == latest_row['ds'], ['ds', 'yhat_lower', 'yhat_upper', 'yhat']].iloc[
                    0].to_dict()

            data = ProphetLatestData(
                ticker=self.ticker,
                date=latest_row['ds'].date(),
                price=latest_row['y'],
                yhat=latest_yhat['yhat'],
                yhat_lower=latest_yhat['yhat_lower'],
                yhat_upper=latest_yhat['yhat_upper'],
            )

            data.trading_action, data.score = scoring(data.price, data.yhat_lower, data.yhat_upper)
        except Exception as e:
            data = ProphetLatestData(
                ticker=self.ticker,
                date=datetime.datetime.now().date(),
                price=None,
                yhat=None,
                yhat_lower=None,
                yhat_upper=None,
            )
        return data

    def generate_latest_data(self, refresh: bool) -> ProphetLatestData:
        """
        ProphetData 객체를 생성하거나 캐시된 데이터를 반환합니다.

        매개변수:
            refresh (bool): 데이터를 새로 생성할지 여부.

        반환값:
            ProphetData: 생성된 ProphetData 객체.
        """
        mylogger.debug("**** Start generate_data... ****")
        redis_name = f'{self.ticker}_{self.REDIS_LATEST_DATA_SUFFIX}'

        mylogger.debug(
            f"redisname: '{redis_name}' / refresh : {refresh}")

        prophet_data = myredis.Base.fetch_and_cache_data(redis_name, refresh, self._make_prophet_latest_data)
        return prophet_data

    def generate_chart_data(self, refresh: bool) -> ProphetChartData:
        """
        1. 현재 주가 (실제 데이터)
            •	df_real['ds'] → x축 (날짜)
            •	df_real['y'] → y축 (실제 주가)

        2. 예측 값 범위 (최소/최대)
            •	df_forecast['ds'] → x축 (날짜)
            •	df_forecast['yhat_lower'] → y축 (최소 예측값)
            •	df_forecast['yhat_upper'] → y축 (최대 예측값)
        """
        mylogger.debug("**** Start generate_prophet_chart_data... ****")
        redis_name = f'{self.ticker}_myprophet_chart_data'

        mylogger.debug(
            f"redisname: '{redis_name}' / refresh : {refresh}")

        def fetch_generate_prophet_chart_data() -> ProphetChartData:
            mylogger.debug(f'initialized: {self.initialized}')
            if not self.initialized:
                self.initializing()

            try:
                # 날짜를 기준으로 합치기 (outer join)
                merged_df = pd.merge(self.df_real, self.df_forecast, on="ds", how="outer")
                # 날짜 정렬
                merged_df = merged_df.sort_values(by="ds").reset_index(drop=True)

                data = ProphetChartData(
                    ticker=self.ticker,
                    labels=merged_df["ds"].tolist(),
                    prices=[{"x": ds, "y": y} for ds, y in zip(merged_df["ds"], merged_df["y"]) if pd.notna(y)], # type: ignore
                    yhats=[{"x": ds, "y": yhat} for ds, yhat in zip(merged_df["ds"], merged_df["yhat"])], # type: ignore
                    yhat_uppers=[{"x": ds, "y": yhat_upper} for ds, yhat_upper in zip(merged_df["ds"], merged_df["yhat_upper"])], # type: ignore
                    yhat_lowers=[{"x": ds, "y": yhat_lower} for ds, yhat_lower in zip(merged_df["ds"], merged_df["yhat_lower"])], # type: ignore
                    is_prophet_up=tsa.common.is_up_by_OLS(self.df_forecast.set_index('ds')['yhat'].to_dict()),
                )
            except Exception:
                data = ProphetChartData(
                    ticker=self.ticker,
                    labels=[],
                    prices=[],
                    yhats=[],
                    yhat_uppers=[],
                    yhat_lowers=[],
                    is_prophet_up=False,
                )
            return data

        prophet_chart_data = myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_prophet_chart_data)
        return prophet_chart_data

    @staticmethod
    def is_valid_date(date_string):
        """
        주어진 문자열이 'YYYY-MM-DD' 형식의 유효한 날짜인지 확인합니다.

        매개변수:
            date_string (str): 확인할 날짜 문자열.

        반환값:
            bool: 유효한 날짜 형식이면 True, 그렇지 않으면 False.
        """
        try:
            # %Y-%m-%d 형식으로 문자열을 datetime 객체로 변환 시도
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            # 변환이 실패하면 ValueError가 발생, 형식이 맞지 않음
            return False

    @staticmethod
    def bulk_get_latest_data(tickers: List[str], refresh: bool) -> Dict[str, ProphetLatestData]:
        return myredis.Base.bulk_get_or_compute(
            tickers,
            lambda ticker: MyProphet(ticker)._make_prophet_latest_data(),
            refresh=refresh,
        )


class CorpProphet(MyProphet):
    """
    기업 코드를 기반으로 주가를 예측하는 Prophet 모델 클래스.

    속성:
        code (str): 기업 코드.
        name (str): 기업명.
    """
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self._code = code
        self.name = myredis.Corps(code, 'c101').get_name()
        super().__init__(ticker=self.code + '.KS')

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self._code = code
        self.name = myredis.Corps(code, 'c101').get_name()
        self.ticker = self.code + '.KS'

    @staticmethod
    def ticker_to_code(ticker:str):
        return ticker[:-3]

    @staticmethod
    def code_to_ticker(code:str):
        return code+'.KS'

    @staticmethod
    def ranking(top: Union[int, str] = 'all', refresh=False) -> OrderedDict:
        mylogger.debug("**** Start prophet ranking ... ****")

        data = {}
        for ticker, latest_data in MyProphet.bulk_get_latest_data(
                [CorpProphet.code_to_ticker(code) for code in myredis.Corps.list_all_codes()], refresh=refresh).items():
            code = CorpProphet.ticker_to_code(ticker)
            mylogger.debug(f'{code} latest_data : {latest_data}')
            mylogger.debug(f'{code} score : {latest_data.score}')
            if latest_data.score is None:
                continue
            else:
                data[code] = latest_data.score

        ranking = OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))

        if top == 'all':
            return ranking
        else:
            if isinstance(top, int):
                return OrderedDict(list(ranking.items())[:top])
            else:
                raise ValueError("top 인자는 'all' 이나 int형 이어야 합니다.")

    @staticmethod
    def bulk_get_latest_data(codes: List[str], refresh: bool) -> Dict[str, ProphetLatestData]:
        ticker_data = MyProphet.bulk_get_latest_data([CorpProphet.code_to_ticker(code) for code in codes], refresh=refresh)
        code_data = {}
        for ticker, data in ticker_data.items():
            code_data[CorpProphet.ticker_to_code(ticker)] = data
        return code_data


class MIProphet(MyProphet):
    """
    특정 MI(Market Indicator) 타입에 따라 주가를 예측하는 Prophet 모델 클래스.

    속성:
        mi_type (str): MI 타입.

    MI 타입:
        WTI (str): 서부 텍사스 중질유(WTI) 선물 지수 (심볼: "CL=F").
        GOLD (str): 금 선물 지수 (심볼: "GC=F").
        SILVER (str): 은 선물 지수 (심볼: "SI=F").
        USD_IDX (str): 미국 달러 인덱스 (심볼: "DX-Y.NYB").
        USD_KRW (str): 달러-원 환율 (심볼: "KRW=X").
        SP500 (str): S&P 500 주가지수 (심볼: "^GSPC").
        KOSPI (str): 코스피 지수 (심볼: "^KS11").
        NIKKEI (str): 닛케이 225 지수 (일본) (심볼: "^N225").
        CHINA (str): 항셍 지수 (홍콩) (심볼: "^HSI").
        IRX (str): 미국 단기 국채 금리 지수 (13주 T-빌 금리) (심볼: "^IRX").
    """
    def __init__(self, mi_type: str):
        assert mi_type in MIs._fields, f"Invalid MI type ({MIs._fields})"
        self._mi_type = mi_type
        super().__init__(ticker=getattr(MIs, mi_type))

    @property
    def mi_type(self) -> str:
        return self._mi_type

    @mi_type.setter
    def mi_type(self, mi_type: str):
        assert mi_type in MIs._fields, f"Invalid MI type ({MIs._fields})"
        self._mi_type = mi_type
        self.ticker = getattr(MIs, mi_type)

    @staticmethod
    def ticker_to_mitype(ticker: str):
        dict_fields = MIs._asdict()
        reverse_map = {value: key for key, value in dict_fields.items()}
        return reverse_map.get(ticker)

    @staticmethod
    def mitype_to_ticker(mi_type: str):
        return getattr(MIs, mi_type)

    @staticmethod
    def bulk_get_latest_data(mi_types: List[str], refresh: bool) -> Dict[str, ProphetLatestData]:
        ticker_data = MyProphet.bulk_get_latest_data([MIProphet.mitype_to_ticker(mi_type) for mi_type in mi_types],
                                                     refresh=refresh)
        mi_data = {}
        for ticker, data in ticker_data.items():
            mi_data[MIProphet.ticker_to_mitype(ticker)] = data
        return mi_data

