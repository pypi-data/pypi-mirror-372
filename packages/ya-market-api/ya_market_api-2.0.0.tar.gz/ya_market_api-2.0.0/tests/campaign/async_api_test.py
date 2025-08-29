from tests.fake_async_session import FakeAsyncSession
from ya_market_api.campaign.async_api import AsyncCampaignAPI
from ya_market_api.campaign.dataclass import CampaignListRequest
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest


class TestAsyncCampaignAPI:
	@pytest.mark.asyncio()
	async def test_get_campaign_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncCampaignAPI(config)
		request = CampaignListRequest(page=10, page_size=100)

		with patch("ya_market_api.campaign.async_api.CampaignListResponse") as CampaignListResponseMock:
			CampaignListResponseMock.model_validate_json = Mock()
			CampaignListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_campaign_list() == "DESERIALIZED DATA"
				CampaignListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.campaign_list()
				assert session.last_call_json == None
				assert session.last_call_params == {}

				assert await api.get_campaign_list(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.campaign_list()
				assert session.last_call_json == None
				assert session.last_call_params == {"page": 10, "pageSize": 100}
