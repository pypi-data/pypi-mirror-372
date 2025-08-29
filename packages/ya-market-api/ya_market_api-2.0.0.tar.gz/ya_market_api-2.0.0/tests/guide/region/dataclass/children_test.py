from ya_market_api.guide.region.dataclass.children import Request

import pytest


class TestRequest:
	def test_page_is_valid(self):
		assert Request.page_is_valid(None) is None
		assert Request.page_is_valid(1) == 1
		assert Request.page_is_valid(10_000) == 10_000

		with pytest.raises(ValueError, match="The page cannot be less than 1 or greater than 10000"):
			Request.page_is_valid(0)

		with pytest.raises(ValueError, match="The page cannot be less than 1 or greater than 10000"):
			Request.page_is_valid(10_001)

	def test_page_size_is_valid(self):
		assert Request.page_size_is_valid(None) is None
		assert Request.page_size_is_valid(1) == 1
		assert Request.page_size_is_valid(10_000) == 10_000

		with pytest.raises(ValueError, match="The page_size cannot be less than 1"):
			Request.page_size_is_valid(0)
