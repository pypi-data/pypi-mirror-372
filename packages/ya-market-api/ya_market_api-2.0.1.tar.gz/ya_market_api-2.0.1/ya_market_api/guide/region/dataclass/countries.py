from ya_market_api.base.dataclass.region import Region

from typing import List

from pydantic.main import BaseModel
from pydantic.fields import Field


class Country(BaseModel):
	code: str = Field(validation_alias="countryCode")
	region: Region


class Response(BaseModel):
	countries: List[Country]
