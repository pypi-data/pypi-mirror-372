from cardlink.types import Bill
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class billStatus:
    """bill/status method"""
    class billStatusMethod(CardLinkBaseMethod):
        id: str

        __return_type__ = Bill
        __api_method__ = "bill/status"
        __request_type__ = "GET"

    async def get_bill(
            self: "cardlink.CardLink",
            id: str
    ) -> Bill:
        """
        Получить статус счета на оплату
        Если счет имеет тип MULTI, то его статус не будет изменяться.

        :param id: Уникальный идентификатор счета

        :return: :class:`Bill` object
        """

        return await self(self.billStatusMethod(**locals()))
