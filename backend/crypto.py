from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


@dataclass(frozen=True)
class Crypto(BaseModel):
    cmc_id: int
    name: str
    price: Decimal
    price_as_of_date: datetime
