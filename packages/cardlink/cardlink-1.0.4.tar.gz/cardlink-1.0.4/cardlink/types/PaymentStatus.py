from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class PaymentStatus(BaseCardLinkTypes):
    """Статус платежа"""

    new: ClassVar[str] = "NEW"
    process: ClassVar[str] = "PROCESS"
    underpaid: ClassVar[str] = "UNDERPAID"
    success: ClassVar[str] = "SUCCESS"
    overpaid: ClassVar[str] = "OVERPAID"
    fail: ClassVar[str] = "FAIL"
