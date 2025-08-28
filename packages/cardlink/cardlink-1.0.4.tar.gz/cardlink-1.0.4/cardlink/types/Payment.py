import datetime
from typing import Any

from pydantic import field_validator

from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.PaymentStatus import PaymentStatus
from cardlink.types.Currency import Currency


class Payment(BaseCardLinkTypes):
    """
    Payment object

    Source: https://cardlink.link/merchant/api#chargeback-resource
    """

    id: str | None = None
    """Уникальный идентификатор платежа"""
    bill_id: str | None = None
    """Уникальный идентификатор счета, которому принадлежит платеж"""
    status: PaymentStatus | str | None = None
    """Статус платежа"""
    amount: int | float | None = None
    """Сумма платежа"""
    commission: int | float | None = None
    """Комиссия"""
    account_amount: int | float | None = None
    """Сумма зачисления на баланс"""
    account_currency_code: Currency | str | None = None
    """Валюта зачисления на баланс"""
    refunded_amount: int |float  | None = None
    """Возвращенная сумма"""
    from_card: str | None = None
    """Номер карты, с которой произошла оплата"""
    currency_in: Currency | str | None = None
    """Валюта, в которой оплачивается счет"""
    created_at: datetime.datetime | None = None
    """Дата и время создания платежа"""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Преобразование строки в datetime object"""
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    async def refresh(self):
        """Обновление информации о платеже"""
        payment = await self._client.get_payment_status(id=self.id)
        self.__dict__ = payment.__dict__
