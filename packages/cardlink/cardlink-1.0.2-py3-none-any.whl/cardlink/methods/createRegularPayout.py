from cardlink.types import Payouts, Crypto
from cardlink.types.Currency import Currency
from cardlink.methods.base import CardLinkBaseMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink


class createRegularPayoutCreditCard:
    """payout/regular/create method (Credit Card)"""
    class createRegularPayoutCreditCardMethod(CardLinkBaseMethod):
        amount: float | int
        currency: Currency | str
        account_identifier: str
        card_holder: str
        account_currency: Currency | str = 'RUB'
        recipient_pays_commission: bool | None = None
        order_id: str | None = None

        __return_type__ = Payouts
        __api_method__ = "payout/regular/create"
        __request_type__ = "POST"

    async def create_payout_credit_card(
            self: "cardlink.CardLink",
            amount: float | int,
            currency: Currency | str,
            account_identifier: str,
            card_holder: str,
            account_currency: Currency | str | None = None,
            recipient_pays_commission: bool | None = None,
            order_id: str | None = None
    ) -> Payouts:
        """
        Отправить средства на указанные реквизиты (Банковская карта)
        Важно: API предоставляется по запросу через службу поддержки.

        Для того чтобы вывести средства с баланса системы необходимо создать выплату. Запрос на выплату может разбиться на несколько выплат в зависимости от используемого аккаунта. В этом случае, в ответе вы получите список с несколькими выплатами.

        :param amount: Сумма выплаты
        :param currency: Валюта
        :param account_identifier: Идентификатор аккаунта: номер карты
        :param card_holder: Держатель карты. Как указано на карте
        :param account_currency: *Options*. Валюта баланса
        :param recipient_pays_commission: *Optional*.
        :param order_id: *Optional*.
        :return: :class:`cardlink.types.Payout` object
        """

        return await self(self.createRegularPayoutCreditCardMethod(**locals()))


class createPersonalPayoutSBP:
    """payout/regular/create method (SBP)"""
    class createPersonalPayoutSBPMethod(CardLinkBaseMethod):
        amount: float | int
        currency: Currency | str
        account_identifier: str
        account_bank: str
        account_currency: Currency | str = 'RUB'
        recipient_pays_commission: bool | None = None
        order_id: str | None = None

        __return_type__ = Payouts
        __api_method__ = "payout/regular/create"
        __request_type__ = "POST"

    async def create_payout_sbp(
            self: "cardlink.CardLink",
            amount: float | int,
            currency: Currency | str,
            account_identifier: str,
            account_bank: str,
            account_currency: Currency | str = 'RUB',
            recipient_pays_commission: bool | None = None,
            order_id: str | None = None
    ) -> Payouts:
        """
        Отправить средства на указанные реквизиты (СБП)
        Важно: API предоставляется по запросу через службу поддержки.

        Для того чтобы вывести средства с баланса системы необходимо создать выплату. Запрос на выплату может разбиться на несколько выплат в зависимости от используемого аккаунта. В этом случае, в ответе вы получите список с несколькими выплатами.

        :param amount: Сумма выплаты
        :param currency: Валюта
        :param account_identifier: Идентификатор аккаунта: номер карты
        :param account_bank: Member ID банка для account_type=sbp.
        :param account_currency: *Options*. Валюта баланса
        :param recipient_pays_commission: *Optional*.
        :param order_id: *Optional*.
        :return: :class:`cardlink.types.Payout` object
        """

        return await self(self.createPersonalPayoutSBPMethod(**locals()))


class createPersonalPayoutCrypto:
    """/payout/regular/create method (Crypto)"""
    class createPersonalPayoutCryptoMethod(CardLinkBaseMethod):
        amount: float | int
        currency: Currency | str
        account_identifier: str
        account_network: Crypto | str
        account_currency: Currency | str = 'RUB'
        recipient_pays_commission: bool | None = None
        order_id: str | None = None

        __return_type__ = Payouts
        __api_method__ = "payout/regular/create"
        __request_type__ = "POST"

    async def create_payout_crypto(
            self: "cardlink.CardLink",
            amount: float | int,
            currency: Currency | str,
            account_identifier: str,
            account_network: Crypto | str,
            account_currency: Currency | str = 'RUB',
            recipient_pays_commission: bool | None = None,
            order_id: str | None = None
    ) -> Payouts:
        """
        Отправить средства на указанные реквизиты (Криптовалюта)
        Важно: API предоставляется по запросу через службу поддержки.

        Для того чтобы вывести средства с баланса системы необходимо создать выплату. Запрос на выплату может разбиться на несколько выплат в зависимости от используемого аккаунта. В этом случае, в ответе вы получите список с несколькими выплатами.

        :param amount: Сумма выплаты
        :param currency: Валюта
        :param account_identifier: Идентификатор аккаунта: номер карты
        :param account_network: Сеть для отправки криптовалюты/токенов.
        :param account_currency: *Options*. Валюта баланса
        :param recipient_pays_commission: *Optional*.
        :param order_id: *Optional*.
        :return: :class:`cardlink.types.Payout` object
        """


        return await self(self.createPersonalPayoutCryptoMethod(**locals()))


class createPersonalPayoutSteam:
    """payout/regular/create method (Steam)"""
    class createPersonalPayoutSteamMethod(CardLinkBaseMethod):
        amount: float | int
        currency: Currency | str
        account_identifier: str
        account_currency: Currency | str = 'RUB'
        recipient_pays_commission: bool | None = None
        order_id: str | None = None

        __return_type__ = Payouts
        __api_method__ = "payout/regular/create"
        __request_type__ = "POST"

    async def create_payout_steam(
            self: "cardlink.CardLink",
            amount: float | int,
            currency: Currency | str,
            account_identifier: str,
            account_currency: Currency | str = 'RUB',
            recipient_pays_commission: bool | None = None,
            order_id: str | None = None
    ) -> Payouts:
        """
        Отправить средства на указанные реквизиты (Steam)
        Важно: API предоставляется по запросу через службу поддержки.

        Для того чтобы вывести средства с баланса системы необходимо создать выплату. Запрос на выплату может разбиться на несколько выплат в зависимости от используемого аккаунта. В этом случае, в ответе вы получите список с несколькими выплатами.

        :param amount: Сумма выплаты
        :param currency: Валюта
        :param account_identifier: Идентификатор аккаунта: номер карты
        :param account_currency: *Options*. Валюта баланса
        :param recipient_pays_commission: *Optional*.
        :param order_id: *Optional*.

        :return: :class:`Payout` object
        """


        return await self(self.createPersonalPayoutSteamMethod(**locals()))
