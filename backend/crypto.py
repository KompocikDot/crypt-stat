from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from asyncpg import Pool
from input import FormInput
from sql_queries import SELECT_CRYPTO_DATA


@dataclass(frozen=True)
class CryptoPriceRow:
    price: Decimal
    volume_24h: Decimal
    volume_change_24h: Decimal
    percent_change_1h: Decimal
    percent_change_24h: Decimal
    percent_change_7d: Decimal
    percent_change_30d: Decimal
    percent_change_60d: Decimal
    percent_change_90d: Decimal
    market_cap: Decimal
    market_cap_dominance: Decimal
    last_updated: datetime

    cryptocurrency_id: int
    currency_id: int

    def to_db_iterable(self):
        return [
            self.price,
            self.volume_24h,
            self.volume_change_24h,
            self.percent_change_1h,
            self.percent_change_24h,
            self.percent_change_7d,
            self.percent_change_30d,
            self.percent_change_60d,
            self.percent_change_90d,
            self.market_cap,
            self.market_cap_dominance,
            self.last_updated,
            self.cryptocurrency_id,
            self.currency_id,
        ]


class CryptoResult:
    def __init__(self, payload: FormInput, db_pool: Pool):
        self.__payload = payload
        self.__db_pool = db_pool

    async def __retrieve_from_db(self, query: tuple[str, list[str]]):
        return await self.__db_pool.fetch(*query)

    async def generate_plot(self):
        return await self.__retrieve_from_db(SELECT_CRYPTO_DATA)
