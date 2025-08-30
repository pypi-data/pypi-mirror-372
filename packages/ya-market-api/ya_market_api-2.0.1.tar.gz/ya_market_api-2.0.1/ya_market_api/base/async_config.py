from ya_market_api.base.config import Config

from aiohttp.client import ClientSession


class AsyncConfig(Config[ClientSession]):
	__slots__ = Config.__slots__
