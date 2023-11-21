import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import matplotlib.pyplot as plt
from asyncpg import Pool, Record
from matplotlib.dates import DateFormatter

from .exceptions import InvalidDataChartType
from .input import FormInput
from .sql_queries import SELECT_CRYPTO_DATA_QUERY

PURPLE_COLOUR = "#4e46e5"
GRAY_COLOUR = "#d1d5db"


@dataclass(frozen=True)
class CryptoPriceRow:
    """Class holding one row of cryptocurrency historical data"""

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
        self._payload = payload
        self._db_pool = db_pool

    async def _retrieve_from_db(self) -> list[Record]:
        return await self._db_pool.fetch(
            SELECT_CRYPTO_DATA_QUERY,
            self._payload.cryptocurrency,
            self._payload.currency,
            self._payload.date_from,
            self._payload.date_until + timedelta(hours=24),  # to get the end of the day
        )

    async def generate_plot(self, cli: bool = True) -> str | None:
        db_data = await self._retrieve_from_db()
        crypto_rows = self._db_res_to_crypto_rows(db_data)

        fig, ax = plt.subplots()

        # filtering x and y axis data
        x_axis = [row.last_updated for row in crypto_rows]
        if crypto_rows and not hasattr(crypto_rows[0], self._payload.data_type):
            raise InvalidDataChartType

        y_axis = [getattr(row, self._payload.data_type) for row in crypto_rows]
        ax.plot(x_axis, y_axis, color=PURPLE_COLOUR)

        # Plot styling
        fig.set_tight_layout(True)
        ax.yaxis.tick_right()
        ax.tick_params(axis="x", rotation=90)
        ax.grid(True, color=GRAY_COLOUR)

        # Setting plot labels and title
        title, y_label = self._create_plot_labels()
        ax.set_title(title)
        ax.set_xlabel("Date and time")
        ax.set_ylabel(y_label)

        # Adding date formatting to plot
        date_formatter = DateFormatter("%d.%m %H:%M")
        ax.xaxis.set_major_formatter(date_formatter)

        if not cli:
            with io.BytesIO() as buf:
                fig.savefig(buf, format="svg")
                buf.seek(0)
                svg = buf.getvalue().decode("utf-8")

            return svg

        return plt.show()

    def _create_plot_labels(self) -> tuple[str, str]:
        match self._payload.data_type:
            case "market_cap":
                title = f"{self._payload.cryptocurrency} market cap"
                y_label = f"Market cap of {self._payload.cryptocurrency}"
            case "price":
                title = f"{self._payload.cryptocurrency} prices"
                y_label = (
                    f"Cost of 1 {self._payload.cryptocurrency} "
                    f"in {self._payload.currency}"
                )
            case "market_cap_dominance":
                title = f"{self._payload.cryptocurrency} market cap dominance"
                y_label = f"Percentage of {self._payload.cryptocurrency} on market"
            case _:
                raise NotImplementedError

        return title, y_label

    @staticmethod
    def _db_res_to_crypto_rows(records: list[Record]) -> list[CryptoPriceRow]:
        return [CryptoPriceRow(**dict(record)) for record in records]
