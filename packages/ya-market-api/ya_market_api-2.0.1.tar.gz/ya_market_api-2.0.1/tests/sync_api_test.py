from ya_market_api.sync_api import SyncAPI
from ya_market_api.generic.requests.auth import APIKeyAuth
from ya_market_api.const import Header
from ya_market_api.guide.sync_api import SyncGuideAPI
from ya_market_api.feedback.sync_api import SyncFeedbackAPI
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch

from requests.sessions import Session


class TestSyncAPI:
	def test___init__(self):
		session = Session()
		config = SyncConfig(session, "")
		api = SyncAPI(config)
		assert api.config.session is session
		assert isinstance(api.guide, SyncGuideAPI)
		assert isinstance(api.feedback, SyncFeedbackAPI)
		assert api.feedback.config.business_id is None

		api.config.business_id = 0
		assert api.feedback.business_id == 0

	def test_build(self):
		with patch.object(SyncAPI, "make_session") as make_session_mock:
			make_session_mock.return_value = "SESSION"
			api = SyncAPI.build("API_KEY")
			assert isinstance(api, SyncAPI)
			assert api.config.session == "SESSION"
			assert api.config.business_id is None
			make_session_mock.assert_called_once_with("API_KEY")

			api = SyncAPI.build("API_KEY", business_id=0)
			assert api.config.business_id == 0

			api = SyncAPI.build("API_KEY", business_id=0, base_url="http://localhost")
			assert api.config.business_id == 0
			assert api.config.base_url == "http://localhost"

	def test_make_session(self):
		session = SyncAPI.make_session("API_KEY")
		assert isinstance(session, Session)
		assert isinstance(session.auth, APIKeyAuth)
		assert session.auth.api_key == "API_KEY"
		assert session.auth.header_label == Header.API_KEY.value
