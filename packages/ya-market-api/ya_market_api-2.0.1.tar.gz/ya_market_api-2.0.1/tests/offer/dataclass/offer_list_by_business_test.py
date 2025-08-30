from ya_market_api.offer.dataclass.offer_list_by_business import Request, Price, PriceWithDiscount
from ya_market_api.offer.const import OfferCardStatusType, CatalogLanguageType

import pytest
from arrow import get as get_arrow


class TestRequest:
	def test_limit_must_be_greater_than_1(self):
		assert Request.limit_must_be_greater_than_0(None) is None
		assert Request.limit_must_be_greater_than_0(10) == 10

		with pytest.raises(ValueError, match="Limit cannot be less than 1"):
			Request.limit_must_be_greater_than_0(0)

	def test_card_statuses_must_be_filled(self):
		assert Request.card_statuses_must_be_filled(None) is None
		assert (
			Request.card_statuses_must_be_filled([OfferCardStatusType.HAS_CARD_CAN_NOT_UPDATE]) == [OfferCardStatusType.HAS_CARD_CAN_NOT_UPDATE]
		)

		with pytest.raises(ValueError, match="Card statuses length cannot be less than 1"):
			Request.card_statuses_must_be_filled([])

	def test_category_ids_must_be_filled(self):
		assert Request.category_ids_must_be_filled(None) is None
		assert Request.category_ids_must_be_filled([1, 2, 3]) == [1, 2, 3]

		with pytest.raises(ValueError, match="Category ids length cannot be less than 1"):
			assert Request.category_ids_must_be_filled([])

	def test_offer_ids_must_be_filled(self):
		assert Request.offer_ids_must_be_filled(None) is None
		assert Request.offer_ids_must_be_filled(["1", "2", "3"]) == ["1", "2", "3"]

		with pytest.raises(ValueError, match="Offer ids length cannot be less than 1"):
			Request.offer_ids_must_be_filled([])

		with pytest.raises(ValueError, match="Offer ids length cannot be greater than 200"):
			Request.offer_ids_must_be_filled(list(map(str, range(201))))

		with pytest.raises(ValueError, match="Offer id length cannot be less than 1"):
			Request.offer_ids_must_be_filled([""])

		with pytest.raises(ValueError, match="Offer id length cannot be greater than 250"):
			Request.offer_ids_must_be_filled(["".join(map(str, range(251)))])

	def test_tags_must_be_filled(self):
		assert Request.tags_must_be_filled(None) is None
		assert Request.tags_must_be_filled(["tag"]) == ["tag"]

		with pytest.raises(ValueError, match="Tags length cannot be less than 1"):
			Request.tags_must_be_filled([])

	def test_vendor_names_must_be_filled(self):
		assert Request.vendor_names_must_be_filled(None) is None
		assert Request.vendor_names_must_be_filled(["vendor"]) == ["vendor"]

		with pytest.raises(ValueError, match="Vendor names length cannot be less than 1"):
			Request.vendor_names_must_be_filled([])

	def test_serialize_language(self):
		request = Request()
		assert request.serialize_language(None) is None
		assert request.serialize_language(CatalogLanguageType.RU) == "RU"

	def test_serialize_card_statuses(self):
		request = Request()
		assert request.serialize_card_statuses(None) is None
		assert request.serialize_card_statuses([]) == []
		assert (
			request.serialize_card_statuses([OfferCardStatusType.HAS_CARD_CAN_UPDATE]) == [OfferCardStatusType.HAS_CARD_CAN_UPDATE.value]
		)

	def test_model_dump_request_params(self):
		request = Request()
		assert request.model_dump_request_params() == {}

		request.limit = 20
		request.page_token = "page-token"
		assert request.model_dump_request_params() == {"limit": 20, "page_token": "page-token"}

		request.offer_ids = ["1", "2", "3"]

		with pytest.warns(UserWarning, match="When using offer_ids, the other query parameters will be ignored"):
			assert request.model_dump_request_params() == {}

	def test_model_dump_request_payload(self):
		request = Request()
		assert request.model_dump_request_payload() == {}

		request.category_ids = [1, 2, 3]
		request.archived = True
		assert request.model_dump_request_payload() == {"categoryIds": [1, 2, 3], "archived": True}

		request.offer_ids = ["1", "2", "3"]

		with pytest.warns(UserWarning, match="When using offer_ids, the other parameters will be ignored"):
			assert request.model_dump_request_payload() == {"offerIds": ["1", "2", "3"]}


class TestPrice:
	def test_datetimes_must_be_arrow(self):
		assert Price.datetimes_must_be_arrow("2025-01-01T00:00:00") == get_arrow(2025, 1, 1)


class TestBasicPrice:
	def test_datetimes_must_be_arrow(self):
		assert PriceWithDiscount.datetimes_must_be_arrow("2025-01-01T00:00:00") == get_arrow(2025, 1, 1)
