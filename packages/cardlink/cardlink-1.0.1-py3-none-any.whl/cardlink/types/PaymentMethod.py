from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class PaymentMethod(BaseCardLinkTypes):
    """Способы оплаты"""

    bank_card: ClassVar[str] = "BANK_CARD"
    sbp: ClassVar[str] = "SBP"
