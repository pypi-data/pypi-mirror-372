import argparse
import asyncio
from analyser2_hj3415.tsseer.mydarts import nbeats_forecast, nhits_forecast, filter_mydarts_by_trend_and_anomaly
from analyser2_hj3415.tsseer.myprophet import prophet_forecast, filter_prophet_by_trend_and_anomaly

from utils_hj3415 import tools
from db2_hj3415.nfs import get_all_tickers

ENGINE_MAP = {
    'prophet': prophet_forecast,
    'nbeats': nbeats_forecast,
    'nhits': nhits_forecast,
}

# 순서대로 달러인덱스, 원달러환율, 미국채3개월물, 원유, 금, 은, sp500, 코스피, 니케이225, 홍콩항셍
MI_TICKERS = ['DX-Y.NYB', 'KRW=X', '^IRX', 'CL=F', 'GC=F', 'SI=F', '^GSPC', '^KS11', '^N225', '^HSI' ]

def handle_cache_many_command(engine: str, tickers: list[str]):
    for ticker in tickers:
        generator = ENGINE_MAP.get(engine)
        if not generator:
            raise ValueError(f"지원하지 않는 tsseer: {engine}")
        data = generator(ticker, refresh=True)
        print(f'{ticker}: {data}')


def handle_cache_mi(engine: str):
    for ticker in MI_TICKERS:
        generator = ENGINE_MAP.get(engine)
        if not generator:
            raise ValueError(f"지원하지 않는 tsseer: {engine}")
        data = generator(ticker, refresh=True)
        print(f'{ticker}: {data}')


def handle_cache_command(engine: str, ticker: str):
    generator = ENGINE_MAP.get(engine)
    if not generator:
        raise ValueError(f"지원하지 않는 tsseer: {engine}")
    data = generator(ticker, refresh=True)
    print(f'{ticker}: {data}')


def main():
    parser = argparse.ArgumentParser(description="Tsseer Commands")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # cache 그룹
    cache_parser = subparsers.add_parser('cache', help='레디스 캐시에 저장 실행')
    cache_subparsers = cache_parser.add_subparsers(dest='cache_type', required=True)

    # ───── cache corp ─────
    cache_corp_parser = cache_subparsers.add_parser('corp', help='기업 코드 캐시')
    cache_corp_parser.add_argument('engine', choices=['prophet', 'nbeats', 'nhits'])
    cache_corp_parser.add_argument('tickers', nargs='*', help="종목티커(예: 005930.KS) 또는 all")

    # ───── cache mi ─────
    cache_me_parser = cache_subparsers.add_parser('mi', help='시장지표 캐시')
    cache_me_parser.add_argument('engine', choices=['prophet', 'nbeats', 'nhits'])
    cache_me_parser.add_argument('tickers', nargs=1, help="'all'만 가능")

    args = parser.parse_args()
    engine = args.engine.lower()

    if args.cache_type == 'corp':
        if len(args.tickers) == 1 and args.tickers[0].lower() == 'all':
            async def main():
                all_corp_ticker = await get_all_tickers()
                handle_cache_many_command(engine, all_corp_ticker)
                if engine == 'nbeats' or engine == 'nhits':
                    await filter_mydarts_by_trend_and_anomaly(all_corp_ticker, "상승", refresh=True)
                    await filter_mydarts_by_trend_and_anomaly(all_corp_ticker, "하락", refresh=True)
                elif engine == 'prophet':
                    await filter_prophet_by_trend_and_anomaly(all_corp_ticker, "상승", refresh=True)
                    await filter_prophet_by_trend_and_anomaly(all_corp_ticker, "하락", refresh=True)

            asyncio.run(main())
        else:
            for ticker in args.tickers:
                handle_cache_command(engine, ticker)
            async def main():
                all_corp_ticker = await get_all_tickers()
                if engine == 'nbeats' or engine == 'nhits':
                    await filter_mydarts_by_trend_and_anomaly(all_corp_ticker, "상승", refresh=True)
                    await filter_mydarts_by_trend_and_anomaly(all_corp_ticker, "하락", refresh=True)
                elif engine == 'prophet':
                    await filter_prophet_by_trend_and_anomaly(all_corp_ticker, "상승", refresh=True)
                    await filter_prophet_by_trend_and_anomaly(all_corp_ticker, "하락", refresh=True)

            asyncio.run(main())

    elif args.cache_type == 'mi':
        if args.tickers[0].lower() == 'all':
            handle_cache_mi(engine)
            async def main():
                if engine == 'nbeats' or engine == 'nhits':
                    await filter_mydarts_by_trend_and_anomaly(MI_TICKERS, "상승", refresh=True)
                    await filter_mydarts_by_trend_and_anomaly(MI_TICKERS, "하락", refresh=True)
                elif engine == 'prophet':
                    await filter_prophet_by_trend_and_anomaly(MI_TICKERS, "상승", refresh=True)
                    await filter_prophet_by_trend_and_anomaly(MI_TICKERS, "하락", refresh=True)
            asyncio.run(main())
        else:
            print("mi 캐시는 'all' 만 허용 됩니다.")