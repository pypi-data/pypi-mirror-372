from tests.fake_async_session import FakeAsyncSession
from ya_market_api.offer.async_api import AsyncOfferAPI
from ya_market_api.offer.dataclass import OfferListByBusinessRequest
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest


class TestAsyncOfferAPI:
	@pytest.mark.asyncio()
	async def test_get_offer_list_by_business(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncOfferAPI(config)
		request = OfferListByBusinessRequest(limit=10, page_token="page-token", category_ids=(1, 2, 3))

		with patch("ya_market_api.offer.async_api.OfferListByBusinessResponse") as OfferListByBusinessResponseMock:
			OfferListByBusinessResponseMock.model_validate_json = Mock()
			OfferListByBusinessResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_offer_list_by_business() == "DESERIALIZED DATA"
				OfferListByBusinessResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.offer_list_by_business(1)
				assert session.last_call_json == {}
				assert session.last_call_params == {}

				assert await api.get_offer_list_by_business(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.offer_list_by_business(1)
				assert session.last_call_json == {"categoryIds": (1, 2, 3)}
				assert session.last_call_params == {"limit": 10, "page_token": "page-token"}
