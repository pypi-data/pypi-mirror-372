from ya_market_api.async_api import AsyncAPI
from ya_market_api.const import Header, BASE_URL
from ya_market_api.guide.async_api import AsyncGuideAPI
from ya_market_api.feedback.async_api import AsyncFeedbackAPI
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch

import pytest
from aiohttp.client import ClientSession


class TestAsyncAPI:
	@pytest.mark.asyncio()
	async def test___init__(self):
		session = ClientSession()
		config = AsyncConfig(session, "", business_id=1)
		api = AsyncAPI(config)
		assert api.config is config
		assert isinstance(api.guide, AsyncGuideAPI)
		assert isinstance(api.feedback, AsyncFeedbackAPI)
		assert api.guide.config is config
		assert api.guide.region.config is config
		assert api.feedback.config is config

		config.business_id = 0
		assert api.feedback.business_id == 0

	@pytest.mark.asyncio()
	async def test_build(self):
		with patch.object(AsyncAPI, "make_session") as make_session_mock:
			make_session_mock.return_value = "SESSION"
			api = await AsyncAPI.build("API_KEY")
			assert isinstance(api, AsyncAPI)
			assert api.config.session == "SESSION"
			assert api.config.business_id is None
			make_session_mock.assert_called_once_with("API_KEY")

			api = await AsyncAPI.build("API_KEY", business_id=0)
			assert api.config.business_id == 0
			assert api.config.base_url == BASE_URL

			api = await AsyncAPI.build("API_KEY", business_id=0, base_url="http://localhost")
			assert api.config.base_url == "http://localhost"

	@pytest.mark.asyncio()
	async def test_make_session(self):
		session = await AsyncAPI.make_session("API_KEY")
		assert isinstance(session, ClientSession)
		assert session.headers == {Header.API_KEY.value: "API_KEY"}

	@pytest.mark.asyncio()
	async def test_close(self):
		api = await AsyncAPI.build("API_KEY")
		await api.close()
		assert api.config.session.closed
