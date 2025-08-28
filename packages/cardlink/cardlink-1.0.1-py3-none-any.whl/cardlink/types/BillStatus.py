from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class BillStatus(BaseCardLinkTypes):
    """
    Статусы счета
    """

    new: ClassVar[str] = "NEW"
    process: ClassVar[str] = "PROCESS"
    underpaid: ClassVar[str] = "UNDERPAID"
    success: ClassVar[str] = "SUCCESS"
    overpaid: ClassVar[str] = "OVERPAID"
    fail: ClassVar[str] = "FAIL"
