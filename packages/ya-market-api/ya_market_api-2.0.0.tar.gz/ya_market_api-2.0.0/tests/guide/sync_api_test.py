from ya_market_api.guide.sync_api import SyncGuideAPI
from ya_market_api.guide.region.sync_api import SyncGuideRegionAPI
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import Mock, patch

from requests.sessions import Session


class TestSyncGuideAPI:
	def test___init__(self):
		session = Session()
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideAPI(config)
		assert isinstance(api.region, SyncGuideRegionAPI)
		assert api.region.session is session

	def test_get_token_info(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "TEXT"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideAPI(config)

		with patch("ya_market_api.guide.sync_api.TokenInfoResponse") as TokenInfoResponseMock:
			TokenInfoResponseMock.model_validate_json = Mock()
			TokenInfoResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_token_info() == "DESERIALIZED DATA"
				TokenInfoResponseMock.model_validate_json.assert_called_once_with("TEXT")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(url=api.router.token_info(), json="")

	def test_get_delivery_services(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "TEXT"
		config = SyncConfig(session, "", business_id=1)
		api = SyncGuideAPI(config)

		with patch("ya_market_api.guide.sync_api.DeliveryServicesResponse") as DeliveryServicesResponseMock:
			DeliveryServicesResponseMock.model_validate_json = Mock()
			DeliveryServicesResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_delivery_services() == "DESERIALIZED DATA"
				DeliveryServicesResponseMock.model_validate_json.assert_called_once_with("TEXT")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(url=api.router.delivery_services())
