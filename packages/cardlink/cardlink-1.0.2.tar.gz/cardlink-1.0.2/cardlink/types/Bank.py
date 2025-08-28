from cardlink.types.base import BaseCardLinkTypes


class Bank(BaseCardLinkTypes):
    """
    Bank object

    Source: https://cardlink.link/merchant/api#sbp-bank-resource
    """

    member_id: int
    """Member ID банка в системе СБП"""
    name: str
    """Название банка"""
    name_en: str
    """Название банка на английском языке"""
    bic: int
    """БИК банка"""
