from cardlink.types.Payment import Payment
from cardlink.types.Meta import Meta
from cardlink.types.Links import Links
from cardlink.types.base import BaseCardLinkTypes


class SearchedPayments(BaseCardLinkTypes):
    """
    Ответ на запрос "search_payment"
    """

    data: list[Payment]
    """Информация о платеже"""
    links: Links
    """Ссылки для пагинации"""
    meta: Meta
    """Мета данные пагинации"""
