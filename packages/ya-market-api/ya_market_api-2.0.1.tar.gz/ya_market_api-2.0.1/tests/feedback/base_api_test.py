from ya_market_api.feedback.base_api import BaseFeedbackAPI
from ya_market_api.exception import BusinessIdError
from ya_market_api.base.config import Config

import pytest


class TestBaseFeedbackAPI:
	def test_business_id(self):
		config = Config(None, "")
		api = BaseFeedbackAPI(config)

		with pytest.raises(BusinessIdError, match="The business_id was not specified"):
			api.business_id

		config.business_id = 512
		assert api.business_id == 512
