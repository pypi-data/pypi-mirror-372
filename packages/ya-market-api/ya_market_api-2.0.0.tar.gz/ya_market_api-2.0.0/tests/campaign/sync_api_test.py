from ya_market_api.campaign.sync_api import SyncCampaignAPI
from ya_market_api.campaign.dataclass import CampaignListRequest
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch, Mock


class TestSyncCampaignAPI:
	def test_get_campaign_list(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, "")
		api = SyncCampaignAPI(config)
		request = CampaignListRequest(page=10, page_size=100)

		with patch("ya_market_api.campaign.sync_api.CampaignListResponse") as CampaignListResponseMock:
			CampaignListResponseMock.model_validate_json = Mock()
			CampaignListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_campaign_list() == "DESERIALIZED DATA"
				CampaignListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(url=api.router.campaign_list(), params={})

				session.get.reset_mock()
				assert api.get_campaign_list(request) == "DESERIALIZED DATA"
				session.get.assert_called_once_with(
					url=api.router.campaign_list(),
					params={"page": 10, "pageSize": 100},
				)
