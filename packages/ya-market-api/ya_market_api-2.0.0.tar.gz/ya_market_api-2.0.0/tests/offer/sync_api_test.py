from ya_market_api.offer.sync_api import SyncOfferAPI
from ya_market_api.offer.dataclass import OfferListByBusinessRequest
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch, Mock


class TestSyncOfferAPI:
	def test_get_offer_list_by_business(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncOfferAPI(config)
		request = OfferListByBusinessRequest(limit=10, page_token="page-token", category_ids=(1, 2, 3))

		with patch("ya_market_api.offer.sync_api.OfferListByBusinessResponse") as OfferListByBusinessResponseMock:
			OfferListByBusinessResponseMock.model_validate_json = Mock()
			OfferListByBusinessResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_offer_list_by_business() == "DESERIALIZED DATA"
				OfferListByBusinessResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(url=api.router.offer_list_by_business(1), params={}, json={})

				session.post.reset_mock()
				assert api.get_offer_list_by_business(request) == "DESERIALIZED DATA"
				session.post.assert_called_once_with(
					url=api.router.offer_list_by_business(1),
					params={"limit": 10, "page_token": "page-token"},
					json={"categoryIds": (1, 2, 3)},
				)
