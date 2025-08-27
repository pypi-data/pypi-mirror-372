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

MIs = {
    'DX-Y.NYB': '달러인덱스',
    'KRW=X': '원달러환율',
    '^IRX': '미국채3개월물',
    'CL=F': '원유',
    'GC=F': '금',
    'SI=F': '은',
    '^GSPC': 'S&P500',
    '^KS11': '코스피',
    '^N225': '니케이225',
    '^HSI': '홍콩항셍',
}

def handle_cache_many_command(engine: str, tickers: list[str]):
    for ticker in tickers:
        generator = ENGINE_MAP.get(engine)
        if not generator:
            raise ValueError(f"지원하지 않는 tsseer: {engine}")
        data = generator(ticker, refresh=True)
        print(f'{ticker}: {data}')


def handle_cache_mi(engine: str):
    for ticker in MIs.keys():
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
                    await filter_mydarts_by_trend_and_anomaly(MIs.keys(), "상승", refresh=True)
                    await filter_mydarts_by_trend_and_anomaly(MIs.keys(), "하락", refresh=True)
                elif engine == 'prophet':
                    await filter_prophet_by_trend_and_anomaly(MIs.keys(), "상승", refresh=True)
                    await filter_prophet_by_trend_and_anomaly(MIs.keys(), "하락", refresh=True)
            asyncio.run(main())
        else:
            print("mi 캐시는 'all' 만 허용 됩니다.")