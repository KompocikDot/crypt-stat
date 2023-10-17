from dataclasses import dataclass
from datetime import date


@dataclass
class FormInput:
    currency: str
    cryptocurrency: str
    date_from: date
    date_until: date
    data_type: str
