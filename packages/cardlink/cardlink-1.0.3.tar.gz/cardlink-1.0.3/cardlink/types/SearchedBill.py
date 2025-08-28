from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.Bill import Bill
from cardlink.types.Meta import Meta
from cardlink.types.Links import Links


class SearchedBill(BaseCardLinkTypes):
    """
    Ответ на запрос "search_bill"
    """

    data: list[Bill]
    """Массив счетов она оплату, удовлетворяющих криетриям запроса"""
    links: Links
    """Ссылки для пагинации"""
    meta: Meta
    """Мета данные пагинации"""
