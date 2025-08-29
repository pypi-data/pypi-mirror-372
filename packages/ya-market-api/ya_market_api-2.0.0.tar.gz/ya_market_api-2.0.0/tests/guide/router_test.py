from ya_market_api.guide.router import GuideRouter


class TestGuideRouter:
	def test_token_info(self):
		router = GuideRouter("")
		assert router.token_info() == "/auth/token"

	def test_delivery_services(self):
		router = GuideRouter("")
		assert router.delivery_services() == "/delivery/services"
