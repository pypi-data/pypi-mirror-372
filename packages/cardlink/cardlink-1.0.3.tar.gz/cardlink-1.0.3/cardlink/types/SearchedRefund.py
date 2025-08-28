from cardlink.types.Refund import Refund
from cardlink.types.Meta import Meta
from cardlink.types.Links import Links
from cardlink.types.base import BaseCardLinkTypes


class SearchedRefund(BaseCardLinkTypes):
    """
    Ответ на запрос "search_refund"
    """

    data: list[Refund]
    """Информация о возвратах"""
    links: Links
    """Ссылки для пагинации"""
    meta: Meta
    """Мета данные пагинации"""
