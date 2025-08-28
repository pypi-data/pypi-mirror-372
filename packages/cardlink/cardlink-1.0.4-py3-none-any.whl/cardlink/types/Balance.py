from decimal import Decimal

from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.Currency import Currency


class Balance(BaseCardLinkTypes):
    """
    Balance object

    Source: https://cardlink.link/merchant/api#balance-resource
    """

    currency: Currency | str
    """Валюта баланса"""
    balance_available: int
    """Доступный баланс"""
    balance_locked: Decimal
    """Заблокированный баланс во время выплаты средств"""
    balance_hold: Decimal
    """Временно удержанный баланс. Переходит в доступный спустя время"""

