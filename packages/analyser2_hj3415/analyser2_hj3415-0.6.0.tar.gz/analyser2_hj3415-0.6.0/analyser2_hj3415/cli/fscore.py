import argparse
import asyncio

from db2_hj3415.valuation import connection, get_all_codes_sync, pretty_print, red as db_red, mil as db_mil, \
    blue as db_blue, growth as db_growth
from db2_hj3415.valuation import RedData, MilData, BlueData, GrowthData
from motor.motor_asyncio import AsyncIOMotorClient

from analyser2_hj3415.fscore import red, mil, blue, growth

from utils_hj3415 import tools

GENERATOR_MAP = {
    'red': red.generate_data,
    'mil': mil.generate_data,
    'blue': blue.generate_data,
    'growth': growth.generate_data,
}

COL_FUNC_MAP = {
    'red': db_red.save,
    'mil': db_mil.save,
    'blue': db_blue.save,
    'growth': db_growth.save,
}

COL_FUNC_MANY_MAP = {
    'red': db_red.save_many,
    'mil': db_mil.save_many,
    'blue': db_blue.save_many,
    'growth': db_growth.save_many,
}

T = RedData | MilData | BlueData | GrowthData

async def generate_data(col: str, target: str) -> T:
    generator = GENERATOR_MAP.get(col)
    if not generator:
        raise ValueError(f"지원하지 않는 컬렉션: {col}")
    data = await generator(target)
    pretty_print(data)
    return data


async def save_data(col: str, data: T):
    func = COL_FUNC_MAP.get(col)
    if not func:
        raise ValueError(f"저장 함수 없음: {col}")

    result = await func(data)
    print(result)


async def generate_many_data(col: str, targets: list[str]) -> dict[str, T]:
    generator = GENERATOR_MAP.get(col)
    if not generator:
        raise ValueError(f"지원하지 않는 컬렉션: {col}")

    results = {}
    for target in targets:
        results[target] = await generator(target)

    pretty_print(results)
    return results


async def save_many_data(col: str, many_data: dict[str, T]):
    func = COL_FUNC_MANY_MAP.get(col)
    if not func:
        raise ValueError(f"저장 함수 없음: {col}")
    result = await func(many_data)
    print(result)


def handle_save_many_command(col: str, targets: list[str]):
    valid_targets = [code for code in targets if tools.is_6digit(code)]
    if not valid_targets:
        print("유효한 종목 코드가 없습니다.")
        return

    async def main():
        many_data = await generate_many_data(col, valid_targets)
        await save_many_data(col, many_data)


    asyncio.run(main())


def handle_save_command(col: str, target: str):
    if not tools.is_6digit(target):
        print(f"잘못된 코드: {target}")
        return

    async def main():
        data = await generate_data(col, target)
        await save_data(col, data)

    asyncio.run(main())


def main():
    parser = argparse.ArgumentParser(description="Fscore Commands")
    subparsers = parser.add_subparsers(dest='command', help='명령어')

    # save 명령
    save_parser = subparsers.add_parser('save', help='데이터 저장 실행')
    save_parser.add_argument('col', type=str, help="컬렉션 이름 : red, mil, growth, blue")
    save_parser.add_argument('targets', nargs='*', help="종목코드 (예: 005930, 000660... and all)")

    args = parser.parse_args()

    if args.command == 'save':
        col = args.col.lower()
        if len(args.targets) == 1 and args.targets[0].lower() == "all":
            handle_save_many_command(col, get_all_codes_sync())
        elif len(args.targets) == 1:
            handle_save_command(col, args.targets[0])
        else:
            handle_save_many_command(col, args.targets)

