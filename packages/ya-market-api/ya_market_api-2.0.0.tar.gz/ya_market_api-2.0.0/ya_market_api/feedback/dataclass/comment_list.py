from ya_market_api.base.dataclass import BaseResponse
from ya_market_api.feedback.const import CommentStatus
from ya_market_api.feedback.dataclass.generic import FeedbackCommentAuthor

from typing import Optional, Collection, Final, Set, Dict, Any, List, overload
from warnings import warn

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict


class Request(BaseModel):
	QUERY_PARAMS: Final[Set[str]] = {"limit", "page_token"}
	S11N_ALIAS_COMMENT_IDS: Final[str] = "commentIds"
	model_config = ConfigDict(arbitrary_types_allowed=True)

	# query params
	limit: Optional[int] = None
	page_token: Optional[str] = None

	# payload
	feedback_id: Optional[int] = Field(default=None, serialization_alias="feedbackId")
	comment_ids: Optional[Collection[int]] = Field(
		default=None,
		serialization_alias=S11N_ALIAS_COMMENT_IDS,
		min_length=1,
		max_length=50,
	)

	@overload
	def __init__(
		self,
		*,
		comment_ids: Collection[int],
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
	) -> None: ...
	@overload
	def __init__(
		self,
		*,
		feedback_id: int,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
	) -> None: ...
	def __init__(
		self,
		*,
		comment_ids: Optional[Collection[int]] = None,
		feedback_id: Optional[int] = None,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
	) -> None:
		super().__init__(
			limit=limit,
			page_token=page_token,
			comment_ids=comment_ids,
			feedback_id=feedback_id,
		)

	def model_dump_request_params(self) -> Dict[str, Any]:
		return self.model_dump(include=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

	def model_dump_request_payload(self) -> Dict[str, Any]:
		result = self.model_dump(exclude=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

		if self.comment_ids is not None and len(result) != 1:
			warn("When using comment_ids, the other parameters will be ignored")
			result = {self.S11N_ALIAS_COMMENT_IDS: result[self.S11N_ALIAS_COMMENT_IDS]}

		if len(result) == 0:
			raise ValueError("feedback_id or comment_ids are required")

		return result


class FeedbackComment(BaseModel):
	author: FeedbackCommentAuthor
	feedback_id: int = Field(validation_alias="feedbackId")
	id: int
	status: CommentStatus
	text: str
	can_modify: Optional[bool] = Field(default=None, validation_alias="canModify")
	parent_id: Optional[int] = Field(default=None, validation_alias="parentId")


class Paging(BaseModel):
	next_page_token: Optional[str] = Field(default=None, validation_alias="nextPageToken")


class Result(BaseModel):
	comments: List[FeedbackComment]
	paging: Optional[Paging] = None


class Response(BaseResponse):
	result: Optional[Result] = None
