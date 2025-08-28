import datetime
from pydantic import field_validator
from cardlink.types.base import BaseCardLinkTypes
from cardlink.types.PayoutStatus import PayoutStatus
from cardlink.types.Currency import Currency


class Payout(BaseCardLinkTypes):
    """
    Payout object

    Source: https://cardlink.link/merchant/api#payout-resource
    """

    id: str | None = None
    """Уникальный идентификатор выплаты"""
    status: PayoutStatus | str | None = None
    """Статус выплаты"""
    order_id: str | None = None
    """Уникальный идентификатор заказа"""
    account_identifier: str | None = None
    """Платежный аккаунт, на который производится выплата"""
    amount: int | float | str | None = None
    """В случае recipient_pays_commission:false поле amount - сумма выплаты с учетом комиссии, в случае recipient_pays_commission:true поле amount - оригинальная сумма выплаты"""
    account_amount: int | float | str | None = None
    """Сумма, списанная с баланса"""
    commission: int | float | str | None = None
    """Комиссия сервиса"""
    account_commission: int | float | str | None = None
    """Комиссия сервиса в валюте баланса"""
    currency: Currency | str | None = None
    """Валюта выплаты"""
    account_currency: Currency | str | None = None
    """Валюта баланса"""
    created_at: datetime.datetime | None = None
    """Дата и время создания выплаты"""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Преобразование строки в datetime object"""
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    async def refresh(self):
        """Обновление информации о выплате"""
        payout = await self._client.get_payout_status(id=self.id)
        self.__dict__ = payout.__dict__
