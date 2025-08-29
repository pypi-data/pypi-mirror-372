from tests.fake_async_session import FakeAsyncSession
from ya_market_api.guide.region.async_api import AsyncGuideRegionAPI
from ya_market_api.guide.region.dataclass import RegionSearchRequest, RegionInfoRequest, RegionChildrenRequest
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest


class TestAsyncGuideRegionAPI:
	@pytest.mark.asyncio()
	async def test_get_region_countries(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncGuideRegionAPI(config)

		with patch("ya_market_api.guide.region.async_api.RegionCountriesResponse") as RegionCountriesResponseMock:
			RegionCountriesResponseMock.model_validate_json = Mock()
			RegionCountriesResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_region_countries() == "DESERIALIZED DATA"
				RegionCountriesResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.region_countries()
				assert session.last_call_json == ""

	@pytest.mark.asyncio()
	async def test_get_search_region(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncGuideRegionAPI(config)
		request = RegionSearchRequest(name="REGION_NAME", limit=100, page_token="PAGE_TOKEN")

		with patch("ya_market_api.guide.region.async_api.RegionSearchResponse") as RegionSearchResponseMock:
			RegionSearchResponseMock.model_validate_json = Mock()
			RegionSearchResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.search_region(request) == "DESERIALIZED DATA"
				RegionSearchResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.region_search()
				assert session.last_call_params == {"name": "REGION_NAME", "limit": 100, "page_token": "PAGE_TOKEN"}

	@pytest.mark.asyncio()
	async def test_get_region_info(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncGuideRegionAPI(config)
		request = RegionInfoRequest(region_id=512)

		with patch("ya_market_api.guide.region.async_api.RegionInfoResponse") as RegionInfoResponseMock:
			RegionInfoResponseMock.model_validate_json = Mock()
			RegionInfoResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_region_info(request) == "DESERIALIZED DATA"
				RegionInfoResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.region_info(512)

	@pytest.mark.asyncio()
	async def test_get_region_children(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncGuideRegionAPI(config)
		request = RegionChildrenRequest(region_id=512, page=1, page_size=100)

		with patch("ya_market_api.guide.region.async_api.RegionChildrenResponse") as RegionChildrenResponseMock:
			RegionChildrenResponseMock.model_validate_json = Mock()
			RegionChildrenResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_region_children(request) == "DESERIALIZED DATA"
				RegionChildrenResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == api.router.region_children(512)
				assert session.last_call_params == {"page": 1, "pageSize": 100}
