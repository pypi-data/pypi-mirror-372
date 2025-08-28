import datetime
from cardlink.types import SearchedPayout
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class searchPayout:
    """payout.search method"""
    class searchPayoutMethod(CardLinkBaseMethod):
        start_date: datetime.datetime | None = None
        finish_date: datetime.datetime | None = None
        per_page: int | None = None
        cursor: str | None = None

        __return_type__ = SearchedPayout
        __api_method__ = "payout/search"
        __request_type__ = "GET"

    async def search_payout(
            self: "cardlink.CardLink",
            start_date: datetime.datetime | None = None,
            finish_date: datetime.datetime | None = None,
            per_page: int | None = None,
            cursor: str | None = None
    ) -> SearchedPayout:
        """
        Получить выплаты

        :param start_date: *Optional*. Начальная дата и время для получения счетов в UTC
        :param finish_date: *Optional*. Конечная дата и время для получения счетов в UTC
        :param per_page: *Optional*. Количество элементов на странице
        :param cursor: *Optional*. Указатель на страницу

        :return: :class:`SearchedPayout` object
        """
        params = locals()

        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S")
        if finish_date:
            params["finish_date"] = finish_date.strftime("%Y-%m-%d %H:%M:%S")

        return await self(self.searchPayoutMethod(**params))
