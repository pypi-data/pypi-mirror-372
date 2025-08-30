from typing import Optional, Generic, TypeVar


T = TypeVar("T")


class Config(Generic[T]):
	__slots__ = "session", "base_url", "business_id", "campaign_id"

	session: T
	base_url: str
	business_id: Optional[int]
	campaign_id: Optional[int]

	def __init__(
		self,
		session: T,
		base_url: str,
		*,
		business_id: Optional[int] = None,
		campaign_id: Optional[int] = None,
	) -> None:
		self.session = session
		self.base_url = base_url
		self.business_id = business_id
		self.campaign_id = campaign_id
