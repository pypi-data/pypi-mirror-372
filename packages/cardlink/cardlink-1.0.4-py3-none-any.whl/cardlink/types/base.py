from pydantic import BaseModel, PrivateAttr, ConfigDict
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import cardlink


class BaseCardLinkTypes(BaseModel):
    """Base object"""

    _client: Optional["cardlink.CardLink"] = PrivateAttr()

    model_config = ConfigDict(
        extra="ignore",
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    def model_post_init(self, ctx: dict) -> None:
        self._client = ctx.get("client")
