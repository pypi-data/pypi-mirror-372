from ya_market_api.base.dataclass import BaseResponse
from ya_market_api.base.const import AuthScope

from typing import Set

from pydantic.main import BaseModel
from pydantic.fields import Field


class APIKey(BaseModel):
	name: str
	auth_scopes: Set[AuthScope] = Field(validation_alias="authScopes")


class Result(BaseModel):
	api_key: APIKey = Field(validation_alias="apiKey")


class Response(BaseResponse):
	result: Result
