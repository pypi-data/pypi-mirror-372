from cardlink.types import Bill, Payment
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class paymentStatus:
    """payment/status method"""
    class paymentStatusMethod(CardLinkBaseMethod):
        id: str
        refunds: bool = True
        chargeback: bool = False

        __return_type__ = Payment
        __api_method__ = "payment/status"
        __request_type__ = "GET"

    async def get_payment(
            self: "cardlink.CardLink",
            id: str,
            refunds: bool | None = None,
            chargeback: bool | None = None
    ) -> Payment:
        """
        Получить статус платежа

        :param id: Уникальный идентификатор платежа
        :param refunds: *Optional*. Осуществлен ли возврата платежа
        :param chargeback: *Optional*. Осуществлен ли чарджбэк платежа

        :return: :class:`Payment` object
        """

        return await self(self.paymentStatusMethod(**locals()))

