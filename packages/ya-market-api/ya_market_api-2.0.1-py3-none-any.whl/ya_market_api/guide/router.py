from ya_market_api.generic.functools import cache
from ya_market_api.base.router import Router


class GuideRouter(Router):
	@cache
	def token_info(self) -> str:
		return f"{self.base_url}/auth/token"

	@cache
	def delivery_services(self) -> str:
		return f"{self.base_url}/delivery/services"
