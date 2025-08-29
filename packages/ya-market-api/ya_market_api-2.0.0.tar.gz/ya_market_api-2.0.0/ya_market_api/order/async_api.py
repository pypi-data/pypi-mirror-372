from ya_market_api.base.async_api_mixin import AsyncAPIMixin
from ya_market_api.order.base_api import BaseOrderAPI
from ya_market_api.order.dataclass import OrderGetRequest, OrderGetResponse


class AsyncOrderAPI(AsyncAPIMixin, BaseOrderAPI):
	async def get_order(self, request: OrderGetRequest) -> OrderGetResponse:
		url = self.router.order_get(self.campaign_id, request.order_id)

		async with self.session.get(url=url) as response:
			self.validate_response(response)
			return OrderGetResponse.model_validate_json(await response.text())

