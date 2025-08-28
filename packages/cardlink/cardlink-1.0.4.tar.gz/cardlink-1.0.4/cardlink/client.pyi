import datetime
from typing import Optional, Literal
from cardlink.types import Refund, Balances, Bill, SearchedBill, SearchedPayout, Currency, Banks
from cardlink.methods import CardLinkBaseMethod
from cardlink.types import SearchedPayments
from cardlink.types.Payout import Payout
from cardlink.types.SearchedRefund import SearchedRefund
from cardlink.types.base import BaseCardLinkTypes
from cardlink.api.aiohttp import AiohttpSession
from cardlink.error import APIError


class CardLink:
    _token: str
    _shop_id: str
    _session: AiohttpSession

    def __init__(self, token: str, shop_id: str) -> None: ...
    def __call__(self, method: CardLinkBaseMethod) -> BaseCardLinkTypes: ...
    def __auth(self) -> None | APIError: ...

    def create_bill(
        self,
        amount: float | int,
        order_id: Optional[str] = ...,
        description: Optional[str] = ...,
        type: Literal['normal', 'multi'] = ...,
        currency_in: Literal['RUB', 'USD', 'EUR'] = ...,
        custom: Optional[str] = ...,
        payer_pays_commission: Literal[0, 1] = ...,
        payer_email: Optional[str] = ...,
        name: Optional[str] = ...,
        ttl: Optional[int] = ...,
        success_url: Optional[str] = ...,
        fail_url: Optional[str] = ...,
        payment_method: Literal["BANK_CARD", "SBP"] = ...,
        request_fields_email: bool = ...,
        request_fields_phone: bool = ...,
        request_fields_name: bool = ...,
        request_fields_comment: bool = ...,
        items: Optional[list] = ...,
    ) -> Bill | APIError: ...
    def get_bill(
        self,
        id: str,
    ) -> Bill | APIError: ...
    def toggle_activity(
        self,
        id: str,
        active: bool
    ) -> Bill | APIError: ...
    def search_bill(
        self,
        start_date: Optional[datetime.datetime] = ...,
        finish_date: Optional[datetime.datetime] = ...,
        shop_id: Optional[str] = ...,
        per_page: Optional[int] = ...,
        cursor: Optional[str] = ...,
    ) -> SearchedBill: ...
    def bill_payments(
            self,
            id: str,
            per_page: Optional[int] = ...,
            cursor: Optional[str] = ...,
    ) -> SearchedPayments: ...
    def refund_full(
        self,
        payment_id: str = ...
    ) -> Refund | APIError: ...
    def refund_partial(
        self,
        payment_id: str = ...,
        amount: int | float = ...,
    ) -> Refund | APIError: ...
    def get_refund(
            self,
            id: str
    ) -> Refund: ...
    def search_refund(
            self,
            payment_id: str = ...,
            start_date: datetime.datetime = ...,
            finish_date: datetime.datetime = ...,
            per_page: int = ...,
            cursor: str = ...
    ) -> SearchedRefund: ...
    def personal_payout(
        self,
        amount: float | int,
        payout_account_id: str,
        account_currency: Optional[Literal['USD', 'RUB', 'EUR']] = ...,
        recipient_pays_commission: Optional[bool] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def create_payout_credit_card(
        self,
        amount: float | int,
        currency: Literal['USD', 'RUB', 'EUR'],
        account_identifier: str,
        card_holder: str,
        account_currency: Literal['USD', 'RUB', 'EUR'] = ...,
        recipient_pays_commission: Optional[bool] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def create_payout_sbp(
        self,
        amount: float | int,
        currency: Literal['USD', 'RUB', 'EUR'],
        account_identifier: str,
        account_bank: str,
        account_currency: Literal['USD', 'RUB', 'EUR'] = ...,
        recipient_pays_commission: Optional[bool] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def create_payout_crypto(
        self,
        amount: float | int,
        currency: Literal['USD', 'RUB', 'EUR'],
        account_identifier: str,
        account_network: Literal['TRX', 'ETH'],
        account_currency: Literal['USD', 'RUB', 'EUR'] = ...,
        recipient_pays_commission: Optional[bool] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def create_payout_steam(
        self,
        amount: float | int,
        currency: Currency | str,
        account_identifier: str,
        account_currency: Currency | str = ...,
        recipient_pays_commission: Optional[bool] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def get_payout(
        self,
        id: Optional[str] = ...,
        order_id: Optional[str] = ...,
    ) -> Payout | APIError: ...
    def search_payout(
        self,
        start_date: Optional[datetime.datetime] = ...,
        finish_date: Optional[datetime.datetime] = ...,
        per_page: Optional[int] = ...,
        cursor: Optional[str] = ...,
    ) -> SearchedPayout: ...
    def get_balance(self) -> Balances | APIError: ...
    def get_banks(self) -> Banks:...
    def search_payments(
        self,
        start_date: Optional[datetime.datetime] = ...,
        finish_date: Optional[datetime.datetime] = ...,
        shop_id: Optional[str] = ...,
        per_page: Optional[int] = ...,
        cursor: Optional[str] = ...,
    ) -> SearchedPayments: ...
    def get_payment(
        self,
        id: Optional[str] = ...,
        refunds: Optional[bool] = ...,
        chargeback: Optional[bool] = ...,
    ) -> Bill: ...
