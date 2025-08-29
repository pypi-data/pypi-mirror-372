from ya_market_api.feedback.const import CommentAuthorType

from typing import Optional

from pydantic.main import BaseModel


class FeedbackCommentAuthor(BaseModel):
	name: Optional[str] = None
	type: Optional[CommentAuthorType] = None
