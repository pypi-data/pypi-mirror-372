from ya_market_api.order.router import OrderRouter


class TestOrderRouter:
	def test_order_get(self):
		assert OrderRouter("").order_get(1, 2) == "/campaigns/1/orders/2"
