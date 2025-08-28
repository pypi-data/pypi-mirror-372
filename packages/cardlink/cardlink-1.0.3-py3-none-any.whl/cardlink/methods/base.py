from abc import ABC
from typing import ClassVar, TypeVar, Type, Generic
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")

class CardLinkBaseMethod(BaseModel, ABC, Generic[T]):
    """Base `CardLink API` method class."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
    )

    __return_type__: Type[T]
    __api_method__: ClassVar[str]
    __request_type__: ClassVar[str]
