from ya_market_api.base.async_api_mixin import AsyncAPIMixin
from ya_market_api.offer.base_api import BaseOfferAPI
from ya_market_api.offer.dataclass import OfferListByBusinessRequest, OfferListByBusinessResponse

from typing import Optional


class AsyncOfferAPI(AsyncAPIMixin, BaseOfferAPI):
	async def get_offer_list_by_business(self, request: Optional[OfferListByBusinessRequest] = None) -> OfferListByBusinessResponse:
		request = request or OfferListByBusinessRequest()
		url = self.router.offer_list_by_business(self.business_id)

		async with self.session.post(
			url=url,
			params=request.model_dump_request_params(),
			json=request.model_dump_request_payload(),
		) as response:
			self.validate_response(response)
			return OfferListByBusinessResponse.model_validate_json(await response.text())
