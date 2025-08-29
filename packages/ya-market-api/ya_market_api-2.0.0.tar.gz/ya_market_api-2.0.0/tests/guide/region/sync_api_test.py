from ya_market_api.guide.region.sync_api import SyncGuideRegionAPI
from ya_market_api.guide.region.dataclass import RegionSearchRequest, RegionInfoRequest, RegionChildrenRequest
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch, Mock


class TestSyncGuideRegionAPI:
	def test_get_region_countries(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideRegionAPI(config)

		with patch("ya_market_api.guide.region.sync_api.RegionCountriesResponse") as RegionCountriesResponseMock:
			RegionCountriesResponseMock.model_validate_json = Mock()
			RegionCountriesResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_region_countries() == "DESERIALIZED DATA"
				RegionCountriesResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(url=api.router.region_countries(), json="")

	def test_search_region(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideRegionAPI(config)
		request = RegionSearchRequest(name="REGION_NAME", limit=100, page_token="PAGE_TOKEN")

		with patch("ya_market_api.guide.region.sync_api.RegionSearchResponse") as RegionSearchResponseMock:
			RegionSearchResponseMock.model_validate_json = Mock()
			RegionSearchResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.search_region(request) == "DESERIALIZED DATA"
				RegionSearchResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					url=api.router.region_search(),
					params={"name": "REGION_NAME", "limit": 100, "page_token": "PAGE_TOKEN"},
				)

	def test_get_region_info(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideRegionAPI(config)
		request = RegionInfoRequest(region_id=512)

		with patch("ya_market_api.guide.region.sync_api.RegionInfoResponse") as RegionInfoResponseMock:
			RegionInfoResponseMock.model_validate_json = Mock()
			RegionInfoResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_region_info(request) == "DESERIALIZED DATA"
				RegionInfoResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(url=api.router.region_info(512))

	def test_get_region_children(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideRegionAPI(config)
		request = RegionChildrenRequest(region_id=512, page=1, page_size=100)

		with patch("ya_market_api.guide.region.sync_api.RegionChildrenResponse") as RegionChildrenResponseMock:
			RegionChildrenResponseMock.model_validate_json = Mock()
			RegionChildrenResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_region_children(request) == "DESERIALIZED DATA"
				RegionChildrenResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					url=api.router.region_children(512),
					params={"page": 1, "pageSize": 100},
				)
