from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.campaign.base_api import BaseCampaignAPI
from ya_market_api.campaign.dataclass import CampaignListRequest, CampaignListResponse

from typing import Optional


class SyncCampaignAPI(SyncAPIMixin, BaseCampaignAPI):
	def get_campaign_list(self, request: Optional[CampaignListRequest] = None) -> CampaignListResponse:
		request = request or CampaignListRequest()
		url = self.router.campaign_list()
		response = self.session.get(
			url=url,
			params=request.model_dump(by_alias=True, exclude_none=True),
		)
		self.validate_response(response)
		return CampaignListResponse.model_validate_json(response.text)
