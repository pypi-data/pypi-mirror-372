import datetime

from pydantic import AnyUrl, field_validator
from cardlink.types.BillTypes import BillTypes
from cardlink.types.Currency import Currency
from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.BillStatus import BillStatus


class Bill(BaseCardLinkTypes):
    """
    Bill object

    Source: https://cardlink.link/merchant/api#bill-resource
    """

    id: str
    """Уникальный идентификатор счета"""
    order_id: str | None = None
    """Уникальный идентификатор заказа на вашей стороне"""
    active: bool | None = None
    """Флаг активности счета"""
    status: BillStatus | str | None = None
    """Статус счета"""
    amount: int | float | None = None
    """Сумма, на которую выставлен счет"""
    type: BillTypes | str | None = None
    """Тип счета"""
    created_at: datetime.datetime | str | None = None
    """Дата и время создания счета"""
    currency_in: Currency | str | None = None
    """Валюта, в которой оплачивается счет"""
    ttl: int | None = None
    """Время жизни счета на оплату в секундах"""
    link_url: AnyUrl | str | None = None
    """Ссылка на страницу с QR кодом"""
    link_page_url: AnyUrl | str | None = None
    """Ссылка на оплату"""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Преобразование строки в datetime object"""
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    async def toggle_active(self):
        """Активация/деактивация счета на оплату"""
        bill = await self._client.toggle_activity(id=self.id, active=(not self.active))
        self.__dict__ = bill.__dict__

    async def refresh(self):
        """Обновление информации о счете"""
        bill = await self._client.get_bill_status(id=self.id)
        self.__dict__ = bill.__dict__
