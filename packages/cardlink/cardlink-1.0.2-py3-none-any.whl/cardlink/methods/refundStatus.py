from cardlink.types.Refund import Refund
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class refundStatus:
    """refund/status method"""
    class refundStatusMethod(CardLinkBaseMethod):
        id: str

        __return_type__ = Refund
        __api_method__ = "refund/status"
        __request_type__ = "GET"

    async def get_refund(
            self: "cardlink.CardLink",
            id: str,
    ) -> Refund:
        """
        Получить статус возврата

        :param id: Уникальный идентификатор возврата

        :return: :class:`Refund` object
        """

        return await self(self.refundStatusMethod(**locals()))
