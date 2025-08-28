from cardlink.types import Refund
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class createFullRefund:
    """refund/full/create method"""
    class createFullRefundMethod(CardLinkBaseMethod):
        payment_id: str
        __api_method__ = "refund/full/create"
        __return_type__ = Refund
        __request_type__ = "POST"

    async def refund_full(
            self: "cardlink.CardLink",
            payment_id: str
    ) -> Refund:
        """
        Сделать полный возврат средств
        Важно: API предоставляется по запросу через службу поддержки.

        :param payment_id: Уникальный идентификатор платежа

        :return: :class:`Refund` object
        """

        return await self(self.createFullRefundMethod(**locals()))
