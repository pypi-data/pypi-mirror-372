from cardlink.types import Refund
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class createPartialRefund:
    """refund/partial/create method"""
    class createPartialRefundMethod(CardLinkBaseMethod):
        payment_id: str
        amount: int | float
        __api_method__ = "refund/partial/create"
        __return_type__ = Refund
        __request_type__ = "POST"


    async def refund_partial(
        self: "cardlink.CardLink",
        payment_id: str,
        amount: int | float
    ) -> Refund:
        """
        Сделать частичный возврат средств
        Важно: API предоставляется по запросу через службу поддержки.

        :param payment_id: Уникальный идентификатор платежа
        :param amount: Сумма частичного возврата

        :return: :class:`Refund` object
        """
        return await self(self.createFullRefundMethod(**locals()))
