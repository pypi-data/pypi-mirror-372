from ya_market_api.generic.functools import cache
from ya_market_api.base.router import Router


class GuideRegionRouter(Router):
	@cache
	def region_countries(self) -> str:
		return f"{self.base_url}/regions/countries"

	@cache
	def region_search(self) -> str:
		return f"{self.base_url}/regions"

	def region_info(self, region_id: int) -> str:
		return f"{self.base_url}/regions/{region_id}"

	def region_children(self, region_id: int) -> str:
		return f"{self.base_url}/regions/{region_id}/children"
