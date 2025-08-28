import ssl
from urllib.parse import urlencode
import certifi
from aiohttp import ClientSession, TCPConnector
from cardlink.api.base import BaseSession
from cardlink.utils.clean_dict import clean_dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cardlink
    import cardlink.methods.base


class AiohttpSession(BaseSession):
    """
    HTTP-сессия на aiohttp
    """

    def __init__(self):
        self._session: ClientSession | None = None

    async def post_request(
            self,
            token,
            method: "cardlink.methods.base.CardLinkBaseMethod",
            client: "cardlink.CardLink"
    ):
        method_data = clean_dict(method.model_dump())

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._session = ClientSession(
            connector=TCPConnector(
                ssl_context=ssl_context,
            ),
        )
        try:
            async with self._session.post(
                url=f"https://cardlink.link/api/v1/{method.__api_method__}",
                json=method_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
            ) as resp:
                response = self._check_response(return_type=method.__return_type__, code=resp.status, data=await resp.json(), api_method=method.__api_method__, client=client)
            return response
        finally:
            await self._session.close()
    async def get_request(
            self,
            token,
            method: "CardLinkBaseMethod",
            client: "CardLink"
    ):
        method_data = clean_dict(method.model_dump())

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._session = ClientSession(
            connector=TCPConnector(
                ssl_context=ssl_context,
            ),
        )
        try:
            async with self._session.get(
                url=f"https://cardlink.link/api/v1/{method.__api_method__}?{urlencode(method_data)}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
            ) as resp:
                response = self._check_response(return_type=method.__return_type__, code=resp.status, data=await resp.json(), api_method=method.__api_method__, client=client)
            return response
        finally:
            await self._session.close()

