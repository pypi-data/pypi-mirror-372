from cardlink.types.base import BaseCardLinkTypes


class Item(BaseCardLinkTypes):
    """
    Список товаров.
    """

    name: str
    price: str
    quantity: str
    category: str
    extra_phone: str
