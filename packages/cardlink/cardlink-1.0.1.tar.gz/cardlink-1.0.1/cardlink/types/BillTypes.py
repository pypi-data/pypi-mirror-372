from typing import ClassVar
from cardlink.types.base import BaseCardLinkTypes


class BillTypes(BaseCardLinkTypes):
    """
    Тип счета
    """

    normal: ClassVar[str] = 'normal'
    multi: ClassVar[str] = 'multi'
