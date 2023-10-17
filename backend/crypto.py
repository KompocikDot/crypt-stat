import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import matplotlib.pyplot as plt
from asyncpg import Pool, Record
from input import FormInput
from sql_queries import SELECT_CRYPTO_DATA_QUERY


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

    async def __retrieve_from_db(self):
        return await self.__db_pool.fetch(
            SELECT_CRYPTO_DATA_QUERY,
            self.__payload.cryptocurrency,
            self.__payload.currency,
            self.__payload.date_from,
            self.__payload.date_until
            + timedelta(hours=24),  # to get the end of the day
        )

    async def generate_plot(self):
        db_data = await self.__retrieve_from_db()
        crypto_rows = self.__db_res_to_crypto_rows(db_data)

        fig, ax = plt.subplots()

        x_axis = [row.last_updated for row in crypto_rows]
        y_axis = [row.price for row in crypto_rows]
        ax.plot(x_axis, y_axis)

        ax.set_title(self.__payload.cryptocurrency)
        ax.set_xlabel("Date and time")
        ax.set_ylabel(
            f"Cost of 1 {self.__payload.cryptocurrency} in {self.__payload.currency}"
        )
        ax.yaxis.tick_right()
        ax.tick_params(axis="x", rotation=90)
        fig.set_tight_layout(True)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="svg")

        buffer.seek(0)
        svg = buffer.getvalue().decode("utf-8")
        buffer.close()

        return svg

    @staticmethod
    def __db_res_to_crypto_rows(records: list[Record]) -> list[CryptoPriceRow]:
        return [CryptoPriceRow(**dict(record)) for record in records]
