from cardlink.types import SearchedPayments
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class billPayments:
    """bill/payments method"""
    class billPaymentsMethod(CardLinkBaseMethod):
        id: str
        per_page: int | None = None
        cursor: str | None = None

        __return_type__ = SearchedPayments
        __api_method__ = "bill/payments"
        __request_type__ = "GET"

    async def bill_payments(
            self: "cardlink.CardLink",
            id: str,
            per_page: int | None = None,
            cursor: str | None = None
    ) -> SearchedPayments:
        """
        Получить платежи, относящиеся к счету на оплату
        Используйте этот метод для получения всех платежей по счету.

        :param id: Уникальный идентификатор счета
        :param per_page: *Optional*. Количество элементов на странице
        :param cursor: *Optional*. Указатель на страницу

        :return: :class:`SearchedPayments` object
        """

        return await self(self.billPaymentsMethod(**locals()))
