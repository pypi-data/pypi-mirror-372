from ya_market_api.base.enum_toolkit import allow_unknown

from enum import Enum


@allow_unknown
class ReactionStatus(Enum):
	ALL = "ALL"
	NEED_REACTION = "NEED_REACTION"


@allow_unknown
class CommentAuthorType(Enum):
	USER = "USER"
	BUSINESS = "BUSINESS"


@allow_unknown
class CommentStatus(Enum):
	PUBLISHED = "PUBLISHED"
	UNMODERATED = "UNMODERATED"
	BANNED = "BANNED"
	DELETED = "DELETED"
