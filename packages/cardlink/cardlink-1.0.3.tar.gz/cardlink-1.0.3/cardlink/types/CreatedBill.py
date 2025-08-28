from cardlink.types.base import BaseCardLinkTypes


class CreatedBill(BaseCardLinkTypes):
    """
    Ответ сервера после запроса на создание счета
    """

    link_url: str
    """Ссылка на страницу с QR кодом"""
    link_page_url: str
    """Ссылка на оплату"""
    bill_id: str
    """Уникальный идентификатор счета"""
