from ya_market_api.base.router import Router
from ya_market_api.base.config import Config

from abc import ABC, abstractmethod
from typing import TypeVar, Generic


RouterT = TypeVar("RouterT", bound=Router)


class API(ABC, Generic[RouterT]):
	config: Config
	router: RouterT

	def __init__(self, config: Config) -> None:
		self.config = config
		self.router = self.make_router(config.base_url)

	@staticmethod
	@abstractmethod
	def make_router(base_url: str) -> RouterT: ...
