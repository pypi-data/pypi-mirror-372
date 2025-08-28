from cardlink.api.aiohttp import AiohttpSession
from cardlink.methods import CardLinkBaseMethod
from cardlink.loggers import client
from cardlink.methods import Methods
from cardlink.error import APIError
from cardlink.utils.check_token import token_validate


class CardLink(Methods):
    """
    Client class providing API methods.

    :param token: CardLink API token
    :param shop_id: SHOP ID
    :param _session: HTTP Session
    """

    def __init__(self, token: str, shop_id: str):
        self._token = token
        self._shop_id = shop_id
        self._session = AiohttpSession()
        self.__auth()


    def __auth(self):
        result_auth = token_validate(token=self._token)
        if not result_auth:
            raise APIError("Authorization failed", 401)
        client.info("Successful authorization in CardLink API")

    async def __call__(
            self,
            method: CardLinkBaseMethod
    ):
        """
        Request method.

        Метод дло отправки запросов к API.

        :param method: CardLinkBaseMethod object
        :return: :class:`BaseCardLinkTypes`
        """
        client.debug(
            "Requesting: /%s with payload %s",
            method.__api_method__,
            method.model_dump_json(),
        )
        if method.__request_type__ == "POST":
            return await self._session.post_request(self._token, method, self)
        return await self._session.get_request(self._token, method, self)



    # async def create_invoice(self, *args, **kwargs):
    #     return await create_invoice_method(self, *args, **kwargs)
    # async def create_full_refund(self, *args, **kwargs):
    #     return await create_full_refund_method(self, *args, **kwargs)
    # async def create_partial_refund(self, *args, **kwargs):
    #     return await create_partial_refund_method(self, *args, **kwargs)
    # async def create_personal_payout(self, *args, **kwargs):
    #     return await create_personal_payout_method(self, *args, **kwargs)
    # async def create_payout_credit_card(self, *args, **kwargs):
    #     return await create_payout_credit_card_method(self, *args, **kwargs)
    # async def create_payout_steam(self, *args, **kwargs):
    #     return await create_payout_steam_method(self, *args, **kwargs)
    # async def create_payout_crypto(self, *args, **kwargs):
    #     return await create_payout_crypto_method(self, *args, **kwargs)
    # async def create_payout_sbp(self, *args, **kwargs):
    #     return await create_payout_sbp_method(self, *args, **kwargs)
    # async def get_balance(self):
    #     return await get_balance_method(self)
    # async def get_invoice_status(self, *args, **kwargs):
    #     return await get_invoice_status_method(self, *args, **kwargs)
    # async def toggle_activity(self, *args, **kwargs):
    #     return await toggle_activity_method(self, *args, **kwargs)
    # async def get_payout_status(self, *args, **kwargs):
    #     return await get_payout_status_method(self, *args, **kwargs)
    # async def search_invoice(self, *args, **kwargs):
    #     return await search_invoice_method(self, *args, **kwargs)
    # async def search_payments(self, *args, **kwargs):
    #     return await search_payments_method(self, *args, **kwargs)
    # async def search_payout(self, *args, **kwargs):
    #     return await search_payout_method(self, *args, **kwargs)
    # async def get_payment_status(self, *args, **kwargs):
    #     return await get_payment_status_method(self, *args, **kwargs)



