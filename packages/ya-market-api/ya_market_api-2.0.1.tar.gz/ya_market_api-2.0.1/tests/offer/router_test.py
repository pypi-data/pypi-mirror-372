from ya_market_api.offer.router import OfferRouter


class TestOfferRouter:
	def test_offer_list_by_business(self):
		assert OfferRouter("").offer_list_by_business("512") == "/businesses/512/offer-mappings"
