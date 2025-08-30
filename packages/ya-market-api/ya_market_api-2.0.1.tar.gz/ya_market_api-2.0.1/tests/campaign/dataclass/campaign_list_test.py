from ya_market_api.campaign.dataclass.campaign_list import Request

import pytest


class TestRequest:
	def test_page_is_valid(self):
		with pytest.raises(ValueError, match="The page cannot be less than 1 or greater than 10000"):
			Request.page_is_valid(0)

		with pytest.raises(ValueError, match="The page cannot be less than 1 or greater than 10000"):
			Request.page_is_valid(10_001)

		assert Request.page_is_valid(None) is None
		assert Request.page_is_valid(512) == 512

