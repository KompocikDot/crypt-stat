import logging
from datetime import datetime

from asyncpg import Pool
from crypto import CryptoPriceRow
from httpx import AsyncClient
from sql_queries import HISTORICAL_DATA_EXISTS_QUERY, INSERT_HISTORICAL_DATA_QUERY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


class Worker:
    API_URL = "https://web-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    def __init__(self, db_pool: Pool) -> None:
        self.__db_pool = db_pool
        self.currencies_codes: dict[str, int] = {}
        self.crypto_codes: dict[str, int] = {}

    async def run(self) -> None:
        self.currencies_codes = await self.__read_currencies_from_db()
        self.crypto_codes = await self.__read_cryptocurrencies_from_db()

        async with AsyncClient() as client:
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

    async def __read_cryptocurrencies_from_db(self) -> dict[str, int]:
        res = await self.__db_pool.fetch("SELECT symbol, id FROM cryptocurrencies")
        return {record["symbol"]: record["id"] for record in res}

    async def __read_currencies_from_db(self) -> dict[str, int]:
        res = await self.__db_pool.fetch("SELECT symbol, id FROM currencies")
        return {record["symbol"]: record["id"] for record in res}

    def __convert_data_to_objects(self, data: dict) -> list[CryptoPriceRow]:
        results: list[CryptoPriceRow] = []

        for crypto_name, crypto_data in data["data"].items():
            cryptocurrency_id = self.crypto_codes[crypto_name]

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
                    currency_id=self.currencies_codes[currency_name],
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
            "symbol": ",".join([key for key in self.crypto_codes.keys()]),
            "convert": ",".join([key for key in self.currencies_codes.keys()]),
        }

        resp = await client.get(self.API_URL, params=params, headers=headers)
        logging.info(f"Scraped data with status: {resp.status_code}")
        return resp.json()

    async def __check_if_exists_in_db(self, params: tuple) -> bool:
        res = await self.__db_pool.fetchval(HISTORICAL_DATA_EXISTS_QUERY, *params)
        return res == 1

    async def __insert_to_db(self, data: list[CryptoPriceRow]):
        return await self.__db_pool.executemany(INSERT_HISTORICAL_DATA_QUERY, data)
