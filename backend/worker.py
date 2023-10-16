import asyncio
import logging
from datetime import datetime

from asyncpg import Pool
from crypto import CryptoPriceRow
from httpx import AsyncClient
from utils import get_db_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


class Worker:
    API_URL = "https://web-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    def __init__(self, worker_delay: int = 360) -> None:
        self.__db_pool: Pool
        self._worker_delay = worker_delay
        self.CURRENCIES_CODES: dict[str, int] = {}
        self.CRYPTO_CODES: dict[str, int] = {}

    async def run(self) -> None:
        self.__db_pool = await get_db_pool()  # noqa
        self.CURRENCIES_CODES = await self.__read_currencies_from_db()
        self.CRYPTO_CODES = await self.__read_cryptocurrencies_from_db()

        async with AsyncClient() as client:
            while True:
                data = await self.__scrape_data(client)
                crypto_data_objects = self.__convert_data_to_objects(data)

                not_in_db: list[CryptoPriceRow] = []
                for obj in crypto_data_objects:
                    to_check = (
                        obj.currency_id,
                        obj.cryptocurrency_id,
                        obj.last_updated,
                    )
                    exists_in_db = await self.__check_if_exists_in_db(to_check)
                    if not exists_in_db:
                        not_in_db.append(obj.to_db_iterable())

                if not_in_db:
                    await self.__insert_to_db(not_in_db)
                    logging.info(f"Successfully inserted {len(not_in_db)} new items")
                else:
                    logging.info("No new items")

                await asyncio.sleep(self._worker_delay)

    async def __read_cryptocurrencies_from_db(self) -> dict[str, int]:
        res = await self.__db_pool.fetch("SELECT symbol, id FROM cryptocurrencies")
        return {record["symbol"]: record["id"] for record in res}

    async def __read_currencies_from_db(self) -> dict[str, int]:
        res = await self.__db_pool.fetch("SELECT symbol, id FROM currencies")
        return {record["symbol"]: record["id"] for record in res}

    def __convert_data_to_objects(self, data: dict) -> list[CryptoPriceRow]:
        results: list[CryptoPriceRow] = []

        for crypto_name, crypto_data in data["data"].items():
            cryptocurrency_id = self.CRYPTO_CODES[crypto_name]

            for currency_name, currency_quote in crypto_data[0]["quote"].items():
                quote: dict = currency_quote
                quote.pop("tvl")
                quote.pop("fully_diluted_market_cap")
                quote["last_updated"] = datetime.strptime(
                    quote["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                obj = CryptoPriceRow(
                    **quote,
                    cryptocurrency_id=cryptocurrency_id,
                    currency_id=self.CURRENCIES_CODES[currency_name],
                )

                results.append(obj)

        return results

    async def __scrape_data(self, client: AsyncClient) -> dict:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/json",
        }

        params = {
            "symbol": ",".join([key for key in self.CRYPTO_CODES.keys()]),
            "convert": ",".join([key for key in self.CURRENCIES_CODES.keys()]),
        }

        resp = await client.get(self.API_URL, params=params, headers=headers)
        logging.info(f"Scraped data with status: {resp.status_code}")
        return resp.json()

    async def __check_if_exists_in_db(self, params: tuple) -> bool:
        res = await self.__db_pool.fetchval(
            "SELECT 1 FROM historical_data "
            "WHERE currency_id = $1 AND cryptocurrency_id = $2 "
            "AND last_updated = $3",
            *params,
        )

        return res == 1

    async def __insert_to_db(self, data: list[CryptoPriceRow]):
        st = """INSERT INTO historical_data (
    price, volume_24h, volume_change_24h, percent_change_1h,
    percent_change_24h, percent_change_7d, percent_change_30d,
    percent_change_60d, percent_change_90d, market_cap,
    market_cap_dominance, last_updated, cryptocurrency_id, currency_id
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
)"""

        return await self.__db_pool.executemany(st, data)
