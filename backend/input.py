from datetime import date

from pydantic import BaseModel


class FormInput(BaseModel):
    output_currencies: list[str]
    cryptocurrencies: list[str]
    date_from: date
    date_until: date
    data_type: str
