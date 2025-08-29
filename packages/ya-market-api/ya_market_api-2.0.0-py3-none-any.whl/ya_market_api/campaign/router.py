from ya_market_api.base.router import Router
from ya_market_api.generic.functools import cache


class CampaignRouter(Router):
	@cache
	def campaign_list(self) -> str:
		return f"{self.base_url}/campaigns"
