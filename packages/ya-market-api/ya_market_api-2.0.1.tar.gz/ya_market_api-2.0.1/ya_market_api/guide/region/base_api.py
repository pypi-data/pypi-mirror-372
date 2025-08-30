from ya_market_api.base.api import API
from ya_market_api.guide.region.router import GuideRegionRouter


class BaseGuideRegionAPI(API[GuideRegionRouter]):
	@staticmethod
	def make_router(base_url: str):
		return GuideRegionRouter(base_url)
