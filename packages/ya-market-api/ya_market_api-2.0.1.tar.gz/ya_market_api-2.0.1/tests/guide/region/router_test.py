from ya_market_api.guide.region.router import GuideRegionRouter


class TestGuideRegionRouter:
	def test_region_countries(self):
		router = GuideRegionRouter("")
		assert router.region_countries() == "/regions/countries"

	def test_region_search(self):
		router = GuideRegionRouter("")
		assert router.region_search() == "/regions"

	def test_region_info(self):
		router = GuideRegionRouter("")
		assert router.region_info(512) == "/regions/512"

	def test_region_children(self):
		router = GuideRegionRouter("")
		assert router.region_children(512) == "/regions/512/children"
