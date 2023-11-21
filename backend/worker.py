import logging
from datetime import datetime

from asyncpg import Pool
from httpx import AsyncClient

from .crypto import CryptoPriceRow
from .sql_queries import (
    HISTORICAL_DATA_EXISTS_QUERY,
    INSERT_HISTORICAL_DATA_QUERY,
    SELECT_CRYPTOCURRENCIES_QUERY,
    SELECT_CURRENCIES_QUERY,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


class Worker:
    API_URL = "https://web-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    def __init__(self, db_pool: Pool) -> None:
        self._db_pool = db_pool
        self.currencies_codes: dict[str, int] = {}
        self.crypto_codes: dict[str, int] = {}

    async def run(self) -> None:
        self.currencies_codes = await self._read_currencies_from_db()
        self.crypto_codes = await self._read_cryptocurrencies_from_db()

        async with AsyncClient(timeout=10) as client:
            data = await self._scrape_data(client)
            crypto_data_objects = self._convert_data_to_objects(data)

            not_in_db: list[CryptoPriceRow] = []
            for obj in crypto_data_objects:
                to_check = (
                    obj.currency_id,
                    obj.cryptocurrency_id,
                    obj.last_updated,
                )
                exists_in_db = await self._check_if_exists_in_db(to_check)
                if not exists_in_db:
                    not_in_db.append(obj.to_db_iterable())

            if not_in_db:
                try:
                    await self._insert_to_db(not_in_db)
                    logging.info(f"Successfully inserted {len(not_in_db)} new items")
                except Exception as e:
                    logging.error(e)

            else:
                logging.info("No new items")

    async def _read_cryptocurrencies_from_db(self) -> dict[str, int]:
        res = await self._db_pool.fetch(SELECT_CRYPTOCURRENCIES_QUERY)
        return {record["symbol"]: record["id"] for record in res}

    async def _read_currencies_from_db(self) -> dict[str, int]:
        res = await self._db_pool.fetch(SELECT_CURRENCIES_QUERY)
        return {record["symbol"]: record["id"] for record in res}

    def _convert_data_to_objects(self, data: dict) -> list[CryptoPriceRow]:
        results: list[CryptoPriceRow] = []

        for crypto_name, crypto_data in data["data"].items():
            cryptocurrency_id = self.crypto_codes[crypto_name]

            for currency_name, currency_quote in crypto_data[0]["quote"].items():
                last_updated = datetime.strptime(
                    currency_quote["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                obj = CryptoPriceRow(
                    price=currency_quote["price"],
                    market_cap=currency_quote["market_cap"],
                    market_cap_dominance=currency_quote["market_cap_dominance"],
                    last_updated=last_updated,
                    cryptocurrency_id=cryptocurrency_id,
                    currency_id=self.currencies_codes[currency_name],
                )
                results.append(obj)

        return results

    async def _scrape_data(self, client: AsyncClient) -> dict:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/json",
        }

        params = {
            "symbol": ",".join(self.crypto_codes.keys()),
            "convert": ",".join(self.currencies_codes.keys()),
        }

        resp = await client.get(self.API_URL, params=params, headers=headers)
        logging.info(f"Scraped data with status: {resp.status_code}")
        return resp.json()

    async def _check_if_exists_in_db(self, params: tuple) -> bool:
        res = await self._db_pool.fetchval(HISTORICAL_DATA_EXISTS_QUERY, *params)
        return res == 1

    async def _insert_to_db(self, data: list[CryptoPriceRow]):
        return await self._db_pool.executemany(INSERT_HISTORICAL_DATA_QUERY, data)
