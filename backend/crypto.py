from decimal import Decimal

from asyncpg import Pool
from input import FormInput
from pydantic import BaseModel


class BaseCurrency(BaseModel):
    id: int
    code: int
    name: str


class Currency(BaseCurrency):
    ...


class Cryptocurrency(BaseCurrency):
    ...


class CryptoPriceRow(BaseModel):
    id: int
    volume: Decimal
    price: Decimal

    cryptocurrency: Cryptocurrency
    currency: Currency


class CryptoResult:
    def __init__(self, payload: FormInput, db_pool: Pool):
        self.__payload = payload
        self.__db_pool = db_pool

    async def __retrieve_from_db(self, query: str):
        return await self.__db_pool.fetch(query)

    async def __get_currencies_codes(self, currencies: list[str]):
        st = "SELECT code FROM currencies WHERE `short_name` in $1"
        return await self.__db_pool.fetch(st, currencies)

    def __convert_payload_to_sql_query(self):
        st = (
            "SELECT id, volume, price, cc.name, cc.code FROM historical_data hd"
            "INNER JOIN cryptocurrencies cc ON cc.id = hd.cryptocurrency_id "
            "INNER JOIN currencies c ON c.id = hd.currency_id"
            "WHERE cc.short_name = $1"
        )

        return st

    async def generate_plot(self):
        statement = self.__convert_payload_to_sql_query()
        return await self.__retrieve_from_db(statement)
