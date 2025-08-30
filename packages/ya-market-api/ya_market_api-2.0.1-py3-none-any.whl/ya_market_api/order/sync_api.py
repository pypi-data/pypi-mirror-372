from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.order.base_api import BaseOrderAPI
from ya_market_api.order.dataclass import OrderGetRequest, OrderGetResponse


class SyncOrderAPI(SyncAPIMixin, BaseOrderAPI):
	def get_order(self, request: OrderGetRequest) -> OrderGetResponse:
		url = self.router.order_get(self.campaign_id, request.order_id)
		response = self.session.get(url=url)
		self.validate_response(response)
		return OrderGetResponse.model_validate_json(response.text)
