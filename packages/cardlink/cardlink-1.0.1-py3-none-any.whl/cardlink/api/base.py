from abc import ABC
from cardlink.error import APIError
from cardlink.types import Payout


class BaseSession(ABC):
    """
    Абстрактный класс.
    """

    def _check_response(self, return_type, code, data, api_method, client):
        if data.get('success') or data.get('success') == 'true':
            data.pop('success')

            if api_method in [
                'payout/dictionaries/sbp_banks',
                'payout/personal/create',
                'payout/regular/create'
            ]:
                data = data['data']
                if isinstance(data, list):
                    return Payout.model_validate(data, context={"client": client})

            return return_type.model_validate(data, context={"client": client})
        raise APIError(message=data.get('message'), code=code)
