from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.Balance import Balance


class Balances(BaseCardLinkTypes):
    """
    Balances object
    """

    balances: list[Balance]
    """Массив, содержащий информацию о балансах мерчанта"""
