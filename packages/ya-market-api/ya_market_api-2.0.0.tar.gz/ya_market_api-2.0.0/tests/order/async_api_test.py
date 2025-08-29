from tests.fake_async_session import FakeAsyncSession
from ya_market_api.order.async_api import AsyncOrderAPI
from ya_market_api.order.dataclass import OrderGetRequest
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest


class TestAsyncOrderAPI:
	@pytest.mark.asyncio()
	async def test_get_order(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", campaign_id=1)		# type: ignore - for testing purposes
		api = AsyncOrderAPI(config)
		request = OrderGetRequest(order_id=512)

		with patch("ya_market_api.order.async_api.OrderGetResponse") as OrderGetResponseMock:
			OrderGetResponseMock.model_validate_json = Mock()
			OrderGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_order(request) == "DESERIALIZED DATA"
				OrderGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.order_get(1, 512)
				assert session.last_call_json == None
				assert session.last_call_params == None
