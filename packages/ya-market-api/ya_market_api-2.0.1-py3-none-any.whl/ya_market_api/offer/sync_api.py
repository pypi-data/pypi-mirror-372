from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.offer.base_api import BaseOfferAPI
from ya_market_api.offer.dataclass import OfferListByBusinessRequest, OfferListByBusinessResponse

from typing import Optional


class SyncOfferAPI(SyncAPIMixin, BaseOfferAPI):
	def get_offer_list_by_business(self, request: Optional[OfferListByBusinessRequest] = None) -> OfferListByBusinessResponse:
		request = request or OfferListByBusinessRequest()
		url = self.router.offer_list_by_business(self.business_id)
		response = self.session.post(
			url=url,
			params=request.model_dump_request_params(),
			json=request.model_dump_request_payload(),
		)
		self.validate_response(response)
		return OfferListByBusinessResponse.model_validate_json(response.text)
