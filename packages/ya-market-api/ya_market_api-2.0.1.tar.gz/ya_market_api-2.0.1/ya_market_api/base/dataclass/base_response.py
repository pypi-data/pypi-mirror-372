from ya_market_api.base.const import Status

from pydantic.main import BaseModel
from pydantic.fields import Field


class BaseResponse(BaseModel):
	status: Status = Field(default=Status.OK)
	result: BaseModel
