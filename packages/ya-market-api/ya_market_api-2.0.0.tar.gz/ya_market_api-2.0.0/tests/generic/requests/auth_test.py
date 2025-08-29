from ya_market_api.generic.requests.auth import APIKeyAuth

from requests.models import Request


class TestAPIKeyAuth:
	def test___call__(self):
		auth = APIKeyAuth("API key")
		request = Request()
		request = auth(request)
		assert request.headers == {"x-api-key": "API key"}

		auth.header_label = "Authorization"
		request = Request()
		request = auth(request)
		assert request.headers == {"Authorization": "API key"}
