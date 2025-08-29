from ya_market_api.base.async_api_mixin import AsyncAPIMixin
from ya_market_api.base.async_config import AsyncConfig
from ya_market_api.exception import InvalidResponseError, AuthorizationError, NotFoundError

from unittest.mock import Mock
from http import HTTPStatus
from typing import Optional, Type

import pytest
from aiohttp.client import ClientSession


class BaseClient:
	def __init__(self, *args, **kwargs) -> None:
		pass


class Client(AsyncAPIMixin, BaseClient):
	pass


class TestAsyncAPIMixin:
	@pytest.mark.asyncio()
	@pytest.mark.parametrize(
		"status, expected_error_type, expected_error_text",
		[
			(HTTPStatus.OK, None, None),
			(HTTPStatus.FORBIDDEN, AuthorizationError, "Unauthorized"),
			(HTTPStatus.UNAUTHORIZED, AuthorizationError, "Unauthorized"),
			(HTTPStatus.NOT_FOUND, NotFoundError, "Resource was not found"),
			(HTTPStatus.INTERNAL_SERVER_ERROR, InvalidResponseError, "Response is not valid"),
		],
	)
	async def test_validate_response(
		self,
		status: HTTPStatus,
		expected_error_type: Optional[Type[Exception]],
		expected_error_text: Optional[str],
	):
		session = ClientSession()
		config = AsyncConfig(session, "", business_id=1)
		api = Client(config)
		response = Mock()
		response.status = status
		response.ok = status < 400

		if expected_error_type is None:
			assert api.validate_response(response) is None
		else:
			with pytest.raises(expected_error_type, match=expected_error_text):
				api.validate_response(response)
