from cardlink.types import Payout
from cardlink.types.base import BaseCardLinkTypes


class Payouts(BaseCardLinkTypes):
    """
    Payouts object.
    """
    data: Payout | list[Payout]
    """Список выводов / вывод"""
