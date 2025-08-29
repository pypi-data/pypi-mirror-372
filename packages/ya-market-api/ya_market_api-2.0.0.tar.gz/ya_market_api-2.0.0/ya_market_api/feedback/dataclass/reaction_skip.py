from ya_market_api.base.const import Status

from typing import Collection

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict


class Request(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	feedback_ids: Collection[int] = Field(serialization_alias="feedbackIds", min_length=1, max_length=50)


class Response(BaseModel):
	status: Status = Field(default=Status.OK)
