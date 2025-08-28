from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class Currency(BaseCardLinkTypes):
    """Доступные валюты"""

    rub: ClassVar[str] = "RUB"
    usd: ClassVar[str] = "USD"
    eur: ClassVar[str] = "EUR"
