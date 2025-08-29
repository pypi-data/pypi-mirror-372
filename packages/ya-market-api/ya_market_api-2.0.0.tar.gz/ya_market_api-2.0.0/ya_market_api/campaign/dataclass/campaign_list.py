from ya_market_api.base.dataclass import FlippingPager
from ya_market_api.campaign.const import APIAvailabilityStatus, PlacementType

from typing import Optional, List

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import field_validator


class Request(BaseModel):
	page: Optional[int] = None
	page_size: Optional[int] = Field(default=None, serialization_alias="pageSize")

	@field_validator("page", mode="after")
	@classmethod
	def page_is_valid(cls, value: Optional[int]) -> Optional[int]:
		if value is None:
			return None

		if value < 1 or value > 10_000:
			raise ValueError("The page cannot be less than 1 or greater than 10000")

		return value


class Business(BaseModel):
	id: Optional[int] = None
	name: Optional[str] = None


class Campaign(BaseModel):
	api_availability: Optional[APIAvailabilityStatus] = Field(default=None, validation_alias="apiAvailability")
	business: Optional[Business] = None
	client_id: Optional[int] = Field(default=None, deprecated=True, validation_alias="clientId")
	domain: Optional[str] = None
	id: Optional[int] = None
	placement_type: Optional[PlacementType] = Field(default=None, validation_alias="placementType")


class Response(BaseModel):
	campaigns: List[Campaign]
	pager: Optional[FlippingPager] = None
