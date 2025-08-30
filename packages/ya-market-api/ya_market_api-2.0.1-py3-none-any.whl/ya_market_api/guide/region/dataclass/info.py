from ya_market_api.base.dataclass.region import Region

from typing import List, Optional

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseModel):
	region_id: int


class ResponsePaging(BaseModel):
	next_page_token: Optional[str] = Field(None, validation_alias="nextPageToken")


class Response(BaseModel):
	regions: List[Region]
	paging: Optional[ResponsePaging] = None
