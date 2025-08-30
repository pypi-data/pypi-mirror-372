from tests.fake_async_session import FakeAsyncSession
from ya_market_api.guide.async_api import AsyncGuideAPI
from ya_market_api.guide.region.async_api import AsyncGuideRegionAPI
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest
from aiohttp.client import ClientSession


class TestAsyncGuideAPI:
	@pytest.mark.asyncio()
	async def test___init__(self):
		session = ClientSession()
		config = AsyncConfig(session, "", business_id=1)
		api = AsyncGuideAPI(config)
		assert isinstance(api.region, AsyncGuideRegionAPI)
		assert api.region.session is session

	@pytest.mark.asyncio()
	async def test_get_token_info(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)				# type: ignore - for testing purposes
		api = AsyncGuideAPI(config)

		with patch("ya_market_api.guide.async_api.TokenInfoResponse") as TokenInfoResponseMock:
			TokenInfoResponseMock.model_validate_json = Mock()
			TokenInfoResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_token_info() == "DESERIALIZED DATA"
				TokenInfoResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.token_info()
				assert session.last_call_json == ""

	@pytest.mark.asyncio()
	async def test_get_delivery_services(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncGuideAPI(config)

		with patch("ya_market_api.guide.async_api.DeliveryServicesResponse") as DeliveryServicesResponseMock:
			DeliveryServicesResponseMock.model_validate_json = Mock()
			DeliveryServicesResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_delivery_services() == "DESERIALIZED DATA"
				DeliveryServicesResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.delivery_services()
				assert session.last_call_params is None
