from datetime import date

from pydantic import BaseModel


class FormInput(BaseModel):
    output_currencies: list[str]
    cryptocurrencies: list[str]
    date_from: date
    date_until: date
    data_type: str

    def convert_from_db_model(self):
        ...

    def convert_to_html(self):
        plot = self.__generate_plot()
        return f'<svg width="100" height="100">{plot}</svg>'

    def __generate_plot(self) -> str:
        return ""
