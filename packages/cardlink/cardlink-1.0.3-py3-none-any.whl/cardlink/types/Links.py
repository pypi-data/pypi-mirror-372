from cardlink.types.base import BaseCardLinkTypes


class Links(BaseCardLinkTypes):
    """
    Ссылки для пагинации
    """

    prev: str | None
    """Ссылка на предыдущую страницу"""
    next: str | None
    """Ссылка на следующую страницу"""
