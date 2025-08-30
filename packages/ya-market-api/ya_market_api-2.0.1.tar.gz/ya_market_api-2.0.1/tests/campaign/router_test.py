from ya_market_api.campaign.router import CampaignRouter


class TestCampaignRouter:
	def test_campaign_list(self):
		router = CampaignRouter("")
		assert router.campaign_list() == "/campaigns"
