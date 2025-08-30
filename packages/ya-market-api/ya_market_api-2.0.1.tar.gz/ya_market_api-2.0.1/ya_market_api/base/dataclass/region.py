from ya_market_api.base.const import RegionType

from typing import List, Optional

from pydantic.main import BaseModel
from pydantic.fields import Field


class Region(BaseModel):
	id: int
	name: str
	type: RegionType
	children: List["Region"] = Field(default_factory=list)
	parent: Optional["Region"] = Field(default=None)
