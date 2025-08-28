from cardlink.types import Banks
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class getBanks:
    """payout/dictionaries/sbp_banks method"""
    class getBanksMethod(CardLinkBaseMethod):
        __return_type__ = Banks
        __api_method__ = "payout/dictionaries/sbp_banks"
        __request_type__ = "GET"

    async def get_banks(
            self: "cardlink.CardLink"
    ) -> Banks:
        """
        Получить список банков, доступных для СБП выплат

        :return: :class:`Banks` object
        """

        return await self(self.getBanksMethod(**locals()))
