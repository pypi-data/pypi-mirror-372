from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.guide.region.base_api import BaseGuideRegionAPI
from ya_market_api.guide.region.dataclass import (
	RegionCountriesResponse, RegionSearchRequest, RegionSearchResponse, RegionInfoRequest, RegionInfoResponse,
	RegionChildrenRequest, RegionChildrenResponse,
)


class SyncGuideRegionAPI(SyncAPIMixin, BaseGuideRegionAPI):
	def get_region_countries(self) -> RegionCountriesResponse:
		url = self.router.region_countries()
		response = self.session.post(url=url, json="")
		self.validate_response(response)
		return RegionCountriesResponse.model_validate_json(response.text)

	def search_region(self, request: RegionSearchRequest) -> RegionSearchResponse:
		url = self.router.region_search()
		response = self.session.get(url=url, params=request.model_dump(exclude_defaults=True, by_alias=True))
		self.validate_response(response)
		return RegionSearchResponse.model_validate_json(response.text)

	def get_region_info(self, request: RegionInfoRequest) -> RegionInfoResponse:
		url = self.router.region_info(request.region_id)
		response = self.session.get(url=url)
		self.validate_response(response)
		return RegionInfoResponse.model_validate_json(response.text)

	def get_region_children(self, request: RegionChildrenRequest) -> RegionChildrenResponse:
		url = self.router.region_children(request.region_id)
		response = self.session.get(
			url=url,
			params=request.model_dump(exclude={"region_id"}, exclude_defaults=True, by_alias=True),
		)
		self.validate_response(response)
		return RegionChildrenResponse.model_validate_json(response.text)
