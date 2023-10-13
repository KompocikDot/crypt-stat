import asyncio

from asyncpg import Pool
from httpx import AsyncClient
from utils import get_db_pool


class Worker:
    CRYPTO_CODES = [
        "BTC",
        "ETH",
        "BNB",
        "XRP",
        "ADA",
        "DOGE",
        "SOL",
        "DOT",
        "LTC",
        "LINK",
    ]
    API_URL = "https://web-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    def __init__(self, worker_delay: int = 360) -> None:
        self.__db_pool: Pool
        self._worker_delay = worker_delay
        self.CURRENCIES_CODES: list[str] = []

    async def run(self) -> None:
        self.__db_pool = await get_db_pool()  # noqa
        self.CURRENCIES_CODES = await self.__read_currencies_from_db()

        async with AsyncClient() as client:
            while True:
                data = await self.__scrape_data(client)
                print(data)
                exists_in_db = await self.__check_in_db(data)
                if not exists_in_db:
                    await self.__insert_to_db([[]])

                await asyncio.sleep(self._worker_delay)

    async def __read_currencies_from_db(self) -> list[str]:
        res = await self.__db_pool.fetch("SELECT cmc_id FROM currencies")
        return [str(record["cmc_id"]) for record in res]

    async def __scrape_data(self, client: AsyncClient) -> dict:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/json",
        }

        params = {
            "symbol": ",".join(self.CRYPTO_CODES),
            "convert_id": ",".join(self.CURRENCIES_CODES),
        }

        resp = await client.get(self.API_URL, params=params, headers=headers)
        return resp.json()

    async def __check_in_db(self, query) -> bool:  # TODO: Add type adnotation there
        return False  # await self.__db_pool.fetchval(query)

    async def __insert_to_db(self, data: list[list[str]]):
        st = """INSERT INTO historical_data (
    price, volume_24h, volume_change_24h, percent_change_1h,
    percent_change_24h, percent_change_7d, percent_change_30d,
    percent_change_60d, percent_change_90d, market_cap,
    market_cap_dominance, last_updated
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
)"""
        return await self.__db_pool.executemany(st, data)
