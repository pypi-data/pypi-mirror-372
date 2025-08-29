from ya_market_api.base.const import Status

from pydantic.main import BaseModel
from pydantic.fields import Field


class Request(BaseModel):
	id: int


class Response(BaseModel):
	status: Status = Field(default=Status.OK)
