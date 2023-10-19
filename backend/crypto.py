import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import matplotlib.pyplot as plt
from asyncpg import Pool, Record
from exceptions import InvalidDataChartType
from input import FormInput
from matplotlib.dates import DateFormatter
from sql_queries import SELECT_CRYPTO_DATA_QUERY


@dataclass(frozen=True)
class CryptoPriceRow:
    price: Decimal
    market_cap: Decimal
    market_cap_dominance: Decimal
    last_updated: datetime

    cryptocurrency_id: int
    currency_id: int

    def to_db_iterable(self):
        return [
            self.price,
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
        y_axis = [getattr(row, self.__payload.data_type) for row in crypto_rows]
        ax.plot(x_axis, y_axis, color="#4e46e5")

        # Plot styling
        fig.set_tight_layout(True)
        ax.yaxis.tick_right()
        ax.tick_params(axis="x", rotation=90)
        ax.grid(True, color="#d1d5db")

        match self.__payload.data_type:
            case "market_cap":
                title = f"{self.__payload.cryptocurrency} market cap"
                y_label = f"Market cap of {self.__payload.cryptocurrency}"
            case "price":
                title = f"{self.__payload.cryptocurrency} prices"
                y_label = (
                    f"Cost of 1 {self.__payload.cryptocurrency} "
                    f"in {self.__payload.currency}"
                )
            case "market_cap_dominance":
                title = f"{self.__payload.cryptocurrency} market cap dominance"
                y_label = f"Percentage of {self.__payload.cryptocurrency} on market"
            case _:
                raise InvalidDataChartType

        ax.set_title(title)
        ax.set_xlabel("Date and time")
        ax.set_ylabel(y_label)

        date_formatter = DateFormatter("%d.%m %H:%M")
        ax.xaxis.set_major_formatter(date_formatter)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="svg")

        buffer.seek(0)
        svg = buffer.getvalue().decode("utf-8")
        buffer.close()

        return svg

    @staticmethod
    def __db_res_to_crypto_rows(records: list[Record]) -> list[CryptoPriceRow]:
        return [CryptoPriceRow(**dict(record)) for record in records]
