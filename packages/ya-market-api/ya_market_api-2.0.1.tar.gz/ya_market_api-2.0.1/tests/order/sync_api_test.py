from ya_market_api.order.sync_api import SyncOrderAPI
from ya_market_api.order.dataclass import OrderGetRequest
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch, Mock


class TestSyncOrderAPI:
	def test_get_order(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", campaign_id=1)
		api = SyncOrderAPI(config)
		request = OrderGetRequest(order_id=512)

		with patch("ya_market_api.order.sync_api.OrderGetResponse") as OrderGetResponseMock:
			OrderGetResponseMock.model_validate_json = Mock()
			OrderGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_order(request) == "DESERIALIZED DATA"
				OrderGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(url=api.router.order_get(1, 512))
