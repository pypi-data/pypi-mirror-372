from requests.auth import AuthBase
from requests.models import Request


class APIKeyAuth(AuthBase):
	def __init__(self, api_key: str, header_label: str = "x-api-key") -> None:
		self.api_key = api_key
		self.header_label = header_label

	def __call__(self, request: Request) -> Request:
		request.headers[self.header_label] = self.api_key
		return request
