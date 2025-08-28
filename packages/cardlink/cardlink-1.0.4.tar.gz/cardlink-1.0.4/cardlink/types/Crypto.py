from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class Crypto(BaseCardLinkTypes):
    """Доступные сети для вывода средств"""

    eth: ClassVar[str] = "ETH"
    trx: ClassVar[str] = "TRX"
