from typing import Optional

from pydantic.main import BaseModel
from pydantic.fields import Field


class FlippingPager(BaseModel):
	current_page: Optional[int] = Field(None, validation_alias="currentPage")
	from_: Optional[int] = Field(None, validation_alias="from")
	page_size: Optional[int] = Field(None, validation_alias="pageSize")
	page_count: Optional[int] = Field(None, validation_alias="pagesCount")
	to: Optional[int] = None
	total: Optional[int] = None
