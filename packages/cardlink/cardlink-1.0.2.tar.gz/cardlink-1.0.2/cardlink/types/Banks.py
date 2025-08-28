from cardlink.types.Bank import Bank
from cardlink.types.base import BaseCardLinkTypes


class Banks(BaseCardLinkTypes):
    """
    Banks object
    """

    data: list[Bank]
    """Список банков"""
