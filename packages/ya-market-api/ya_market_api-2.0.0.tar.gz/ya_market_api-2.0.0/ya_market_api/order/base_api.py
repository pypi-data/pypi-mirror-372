from ya_market_api.base.api import API
from ya_market_api.exception import CampaignIdError
from ya_market_api.order.router import OrderRouter


class BaseOrderAPI(API[OrderRouter]):
	@property
	def campaign_id(self) -> int:
		if self.config.campaign_id is None:
			raise CampaignIdError("The campaign_id was not specified")

		return self.config.campaign_id

	@staticmethod
	def make_router(base_url: str) -> OrderRouter:
		return OrderRouter(base_url)
