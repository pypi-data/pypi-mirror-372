from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class RefundType(BaseCardLinkTypes):
    """Тип возврата"""

    payment: ClassVar[str] = 'payment'
