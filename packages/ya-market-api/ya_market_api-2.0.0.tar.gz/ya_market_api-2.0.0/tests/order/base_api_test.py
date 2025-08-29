from ya_market_api.order.base_api import BaseOrderAPI
from ya_market_api.base.config import Config
from ya_market_api.exception import CampaignIdError

import pytest


class TestBaseOrderAPI:
	def test_campaign_id(self):
		config = Config(None, "")
		api = BaseOrderAPI(config)

		with pytest.raises(CampaignIdError, match="The campaign_id was not specified"):
			api.campaign_id

		config.campaign_id = 512
		assert api.campaign_id == 512
