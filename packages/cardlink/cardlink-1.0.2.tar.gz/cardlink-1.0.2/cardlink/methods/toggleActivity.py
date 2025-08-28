from cardlink.types import Bill
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class toggleActivity:
    class toggleActivityMethod(CardLinkBaseMethod):
        id: str
        active: bool

        __return_type__ = Bill
        __api_method__ = "bill/toggle_activity"
        __request_type__ = "POST"

    async def toggle_activity(
            self: "cardlink.CardLink",
            id: str,
            active: bool
    ) -> Bill:
        """
        Активировать/деактивировать счет на оплату
        Деактивация счета может быть полезна для ручного отключения платежной ссылки с типом MULTI, т.к. такой тип платежных ссылок не меняет свой статус после оплаты и может быть оплачен еще сколько угодно раз.

        :param id: Уникальный идентификатор счета
        :param active: False - деактивировать счет, True - активировать счет

        :return: :class:`Bill` object
        """
        params = locals()

        params["active"] = int(params["active"])

        return await self(self.toggleActivityMethod(**params))
