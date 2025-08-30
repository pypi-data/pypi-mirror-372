from ya_market_api.base.dataclass.region import Region

from typing import Optional, List

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseModel):
	name: str
	limit: Optional[int] = None
	page_token: Optional[str] = None


class ResponsePaging(BaseModel):
	next_page_token: Optional[str] = Field(default=None, validation_alias="nextPageToken")


class Response(BaseModel):
	regions: List[Region]
	paging: Optional[ResponsePaging] = None
