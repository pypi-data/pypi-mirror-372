from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class PayoutStatus(BaseCardLinkTypes):
    """Статус выплаты"""

    new: ClassVar[str] = "NEW"
    moderating: ClassVar[str] = "MODERATING"
    process: ClassVar[str] = "PROCESS"
    fail: ClassVar[str] = "FAIL"
    error: ClassVar[str] = "ERROR"
    success: ClassVar[str] = "SUCCESS"
    declined: ClassVar[str] = "DECLINED"
