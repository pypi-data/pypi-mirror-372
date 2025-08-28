from typing import Literal
from cardlink.types import Payouts
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class createPersonalPayout:
    """payout/personal/create method"""
    class createPersonalPayoutMethod(CardLinkBaseMethod):
        amount: float | int
        payout_account_id: str
        account_currency: Literal['USD', 'RUB', 'EUR'] | None = None
        recipient_pays_commission: bool | None = None
        order_id: str | None = None

        __return_type__ = Payouts
        __api_method__ = "payout/personal/create"
        __request_type__ = "POST"

    async def personal_payout(
            self: "cardlink.CardLink",
            amount: float | int,
            payout_account_id: str,
            account_currency: Literal['USD', 'RUB', 'EUR'] | None = None,
            recipient_pays_commission: bool | None = None,
            order_id: str | None = None
    ) -> Payouts:
        """
        Создать выплату на привязанный платежный аккаунт
        Важно: API предоставляется по запросу через службу поддержки.

        Для того чтобы вывести средства с баланса системы необходимо создать выплату. Запрос на выплату может разбиться на несколько выплат в зависимости от используемого аккаунта. В этом случае, в ответе вы получите список с несколькими выплатами.

        :param amount: Сумма выплаты
        :param payout_account_id: Уникальный идентификатор платежного аккаунта, на который будет произведена выплата
        :param account_currency: *Optional*. Валюта баланса, с которого необходимо списать средства за выплату
        :param recipient_pays_commission: *Optional*. Параметр отвечающий за то, кто платит комиссию (true-комиссию платит получающий выплату, если false-то комиссия будет вычтена с баланса аккаунта)
        :param order_id: *Optional*. Уникальный идентификатор заказа

        :return: :class:`Payout` object
        """
        return await self(self.createPersonalPayoutMethod(**locals()))
