from ya_market_api.base.config import Config

from requests.sessions import Session


class SyncConfig(Config[Session]):
	__slots__ = Config.__slots__
