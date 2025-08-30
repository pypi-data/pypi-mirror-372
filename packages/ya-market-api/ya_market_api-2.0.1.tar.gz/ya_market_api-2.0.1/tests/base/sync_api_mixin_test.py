from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.base.sync_config import SyncConfig
from ya_market_api.exception import InvalidResponseError, AuthorizationError, NotFoundError

from http import HTTPStatus
from typing import Type, Optional

import pytest
from requests.sessions import Session
from requests.models import Response


class BaseClient:
	def __init__(self, *args, **kwargs) -> None:
		pass


class Client(SyncAPIMixin, BaseClient):
	pass


class TestSyncAPIMixin:
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
	def test_validate_response(
		self,
		status: HTTPStatus,
		expected_error_type: Optional[Type[Exception]],
		expected_error_text: Optional[str],
	):
		session = Session()
		config = SyncConfig(session, "")
		api = Client(config)
		response = Response()
		response.status_code = status

		if expected_error_type is None:
			assert api.validate_response(response) is None
		else:
			with pytest.raises(expected_error_type, match=expected_error_text):
				api.validate_response(response)
