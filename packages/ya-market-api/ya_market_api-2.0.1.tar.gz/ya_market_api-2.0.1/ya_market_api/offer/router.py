from ya_market_api.base.router import Router


class OfferRouter(Router):
	def offer_list_by_business(self, business_id) -> str:
		return f"{self.base_url}/businesses/{business_id}/offer-mappings"
