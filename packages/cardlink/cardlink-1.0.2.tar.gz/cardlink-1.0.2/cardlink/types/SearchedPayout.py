from cardlink.types.Payout import Payout
from cardlink.types.Meta import Meta
from cardlink.types.Links import Links
from cardlink.types.base import BaseCardLinkTypes


class SearchedPayout(BaseCardLinkTypes):
    """
    Ответ на запрос "search_payout"
    """

    data: list[Payout]
    """Массив выплат"""
    links: Links
    """Ссылки для пагинации"""
    meta: Meta
    """Мета данные пагинации"""
