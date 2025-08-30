from ya_market_api.base.api import API
from ya_market_api.campaign.router import CampaignRouter


class BaseCampaignAPI(API[CampaignRouter]):
	@staticmethod
	def make_router(base_url: str) -> CampaignRouter:
		return CampaignRouter(base_url)
