from cardlink.types import Balances
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class getBalance:
    """merchant/balance method"""
    class getBalanceMethod(CardLinkBaseMethod):
        __return_type__ = Balances
        __api_method__ = "merchant/balance"
        __request_type__ = "GET"

    async def get_balance(
            self: "cardlink.CardLink"
    ) -> Balances:
        """
        Получить баланс

        :return: :class:`Balances` object
        """

        return await self(self.getBalanceMethod(**locals()))
