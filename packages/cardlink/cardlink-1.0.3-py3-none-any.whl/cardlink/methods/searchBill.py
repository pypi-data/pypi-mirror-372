import datetime
from cardlink.types import SearchedBill
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class searchBill:
    """bill/search method"""
    class searchBillMethod(CardLinkBaseMethod):
        start_date: datetime.datetime | None = None
        finish_date: datetime.datetime | None = None
        shop_id: str | None = None
        per_page: int | None = None
        cursor: str | None = None

        __return_type__ = SearchedBill
        __api_method__ = "bill/search"
        __request_type__ = "GET"

    async def search_bill(
            self: "cardlink.CardLink",
            start_date: datetime.datetime | None = None,
            finish_date: datetime.datetime | None = None,
            shop_id: str | None = None,
            per_page: int | None = None,
            cursor: str | None = None,
    ) -> SearchedBill:
        """
        Найти счета на оплату
        Поиск по счетам. Можно указать периоды времени или магазин, чтобы найти нужные счета.

        :param start_date: *Optional*. Начальная дата и время для получения счетов в UTC
        :param finish_date: *Optional*. Конечная дата и время для получения счетов в UTC
        :param shop_id: *Optional*. Уникальный идентификатор магазина
        :param per_page: *Optional*. Количество элементов на странице
        :param cursor: *Optional*. Указатель на страницу

        :return: :class:`SearchedBill` object
        """
        params = locals()

        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
        if finish_date:
            params["finish_date"] = finish_date.strftime("%Y-%m-%d %H:%M:%S")
        if not shop_id:
            params["shop_id"] = self._shop_id

        return await self(self.searchBillMethod(**params))
