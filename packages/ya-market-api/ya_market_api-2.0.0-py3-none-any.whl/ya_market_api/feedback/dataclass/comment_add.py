from ya_market_api.base.dataclass import BaseResponse
from ya_market_api.feedback.const import CommentStatus
from ya_market_api.feedback.dataclass.generic import FeedbackCommentAuthor

from typing import Optional

from pydantic.main import BaseModel
from pydantic.fields import Field


class RequestComment(BaseModel):
	parent_id: Optional[int] = Field(default=None, serialization_alias="parentId")
	text: str = Field(min_length=1)


class Request(BaseModel):
	feedback_id: int = Field(serialization_alias="feedbackId")
	comment: RequestComment

	@classmethod
	def create(cls, feedback_id: int, text: str, parent_id: Optional[int] = None) -> "Request":
		return cls(feedback_id=feedback_id, comment=RequestComment(parent_id=parent_id, text=text))


class Result(BaseModel):
	id: int
	author: FeedbackCommentAuthor
	feedback_id: int = Field(validation_alias="feedbackId")
	status: CommentStatus
	text: str
	can_modify: Optional[bool] = Field(default=None, validation_alias="canModify")
	parent_id: Optional[int] = Field(default=None, validation_alias="parentId")


class Response(BaseResponse):
	result: Optional[Result] = None
