from cardlink.types.base import BaseCardLinkTypes


class Meta(BaseCardLinkTypes):
    """
    Мета данные пагинации
    """

    path: str
    """Ссылка на страницу без курсора"""
    per_page: int
    """Количество элементов на странице"""
    prev_cursor: str | None = None
    """Указатель на предыдущую страницу"""
    next_cursor: str | None = None
    """Указатель на следующую страницу"""
