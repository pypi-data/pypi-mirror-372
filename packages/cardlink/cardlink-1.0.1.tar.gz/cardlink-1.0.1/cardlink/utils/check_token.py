import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import certifi
from cardlink.error import APIError


def token_validate(token) -> bool:
    url = f"https://cardlink.link/api/v1/merchant/balance"
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        request = Request(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        with urlopen(request, context=ssl_context) as resp:
            status_code = resp.getcode()
            body = resp.read()
            return True
    except HTTPError as e:
        status_code = e.code
        body = e.read()
        raise APIError(message=body, code=status_code)
