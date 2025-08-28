from cardlink.types import Payout
from cardlink.error import APIError
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class payoutStatus:
    """payout/status method"""
    class payoutStatusMethod(CardLinkBaseMethod):
        id: str | None = None
        order_id: str | None = None

        __return_type__ = Payout
        __api_method__ = "payout/status"
        __request_type__ = "GET"

    async def get_payout(
            self: "cardlink.CardLink",
            id: str | None = None,
            order_id: str | None = None
    ) -> Payout:
        """
        Получить статус выплаты

        :param id: Уникальный идентификатор выплаты. Обязателен, если не передан order_id
        :param order_id: Уникальный идентификатор заказа. Обязателен, если не передан id

        :return::class:`Payout` object
        """
        if id is None and order_id is None:
            return APIError(message="Argument not passed")

        return await self(self.payoutStatusMethod(**locals()))
