import datetime
from cardlink.types import SearchedRefund
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class searchRefund:
    """refund/search method"""
    class searchRefundMethod(CardLinkBaseMethod):
        payment_id: str | None = None
        start_date: datetime.datetime | None = None
        finish_date: datetime.datetime | None = None
        per_page: int | None = None
        cursor: str | None = None

        __return_type__ = SearchedRefund
        __api_method__ = "refund/search"
        __request_type__ = "GET"

    async def search_refund(
            self: "cardlink.CardLink",
            payment_id: str | None = None,
            start_date: datetime.datetime | None = None,
            finish_date: datetime.datetime | None = None,
            per_page: int | None = None,
            cursor: str | None = None,
    ) -> SearchedRefund:
        """
        Получить возвраты

        :param payment_id: *Optional*. ID платежа
        :param start_date: *Optional*. Начальная дата и время для получения возвратов в UTC
        :param finish_date: *Optional*. Конечная дата и время для получения возвратов в UTC
        :param per_page: *Optional*. Количество элементов на странице
        :param cursor: *Optional*. Указатель на страницу

        :return: :class:`SearchedRefund` object
        """
        params = locals()

        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
        if finish_date:
            params["finish_date"] = finish_date.strftime("%Y-%m-%d %H:%M:%S")

        return await self(self.searchRefundMethod(**params))
