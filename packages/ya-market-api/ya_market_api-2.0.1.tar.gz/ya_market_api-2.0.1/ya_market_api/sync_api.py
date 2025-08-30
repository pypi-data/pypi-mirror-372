from ya_market_api.const import Header, BASE_URL
from ya_market_api.generic.requests.auth import APIKeyAuth
from ya_market_api.guide.sync_api import SyncGuideAPI
from ya_market_api.feedback.sync_api import SyncFeedbackAPI
from ya_market_api.offer.sync_api import SyncOfferAPI
from ya_market_api.campaign.sync_api import SyncCampaignAPI
from ya_market_api.order.sync_api import SyncOrderAPI
from ya_market_api.base.sync_config import SyncConfig

from typing import Optional

from requests.sessions import Session


class SyncAPI:
	guide: SyncGuideAPI
	feedback: SyncFeedbackAPI
	offer: SyncOfferAPI
	campaign: SyncCampaignAPI
	order: SyncOrderAPI
	config: SyncConfig

	def __init__(self, config: SyncConfig) -> None:
		self.config = config
		self.guide = SyncGuideAPI(config)
		self.feedback = SyncFeedbackAPI(config)
		self.offer = SyncOfferAPI(config)
		self.campaign = SyncCampaignAPI(config)
		self.order = SyncOrderAPI(config)

	@classmethod
	def build(
		cls,
		api_key: str,
		*,
		base_url: str = BASE_URL,
		business_id: Optional[int] = None,
		campaign_id: Optional[int] = None,
	) -> "SyncAPI":
		config = SyncConfig(
			cls.make_session(api_key),
			base_url,
			business_id=business_id,
			campaign_id=campaign_id,
		)

		return cls(config)

	@staticmethod
	def make_session(api_key: str) -> Session:
		session = Session()
		session.auth = APIKeyAuth(api_key, Header.API_KEY.value)

		return session
