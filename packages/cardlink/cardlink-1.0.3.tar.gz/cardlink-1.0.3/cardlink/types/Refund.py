import datetime
from pydantic import field_validator
from cardlink.types.RefundStatus import RefundStatus
from cardlink.types.Currency import Currency
from cardlink.types.RefundType import RefundType
from cardlink.types.base import BaseCardLinkTypes


class Refund(BaseCardLinkTypes):
    """
    Refund object

    Source: https://cardlink.link/merchant/api#refund-resource
    """

    id: str | None = None
    """Уникальный идентификатор возврата"""
    status: RefundStatus | str | None = None
    """Статус возврата"""
    amount: int | float | None = None
    """Сумма возврата"""
    currency_in: Currency | str | None = None
    """Валюта"""
    entity_type: str | RefundType | None = None
    """Тип возврата"""
    entity_id: str | None = None
    """Уникальный идентификатор платежа, по которому производится возврат"""
    created_at: datetime.datetime | None = None
    """Дата и время создания возврата"""

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Преобразование строки в datetime object"""
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    async def refresh(self):
        """Обновление информации о возврате"""
        refund = await self._client.get_refund_status(id=self.id)
        self.__dict__ = refund.__dict__
