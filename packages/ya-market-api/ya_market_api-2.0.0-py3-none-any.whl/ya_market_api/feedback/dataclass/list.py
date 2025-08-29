from ya_market_api.feedback.const import ReactionStatus
from ya_market_api.base.dataclass import BaseResponse

from typing import Optional, Collection, Final, Set, Dict, Any, List, overload
from warnings import warn

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from pydantic.functional_validators import field_validator
from pydantic.functional_serializers import field_serializer
from arrow import Arrow, get as get_arrow


class Request(BaseModel):
	QUERY_PARAMS: Final[Set[str]] = {"limit", "page_token"}		# pydantic model_dump requires set
	S11N_ALIAS_FEEDBACK_IDS: Final[str] = "feedbackIds"
	model_config = ConfigDict(arbitrary_types_allowed=True)

	# query params
	limit: Optional[int] = Field(default=None)
	page_token: Optional[str] = None

	# payload
	datetime_from: Optional[Arrow] = Field(default=None, serialization_alias="dateTimeFrom")
	datetime_to: Optional[Arrow] = Field(default=None, serialization_alias="dateTimeTo")
	paid: Optional[bool] = None
	rating_values: Optional[Collection[int]] = Field(default=None, serialization_alias="ratingValues")
	reaction_status: Optional[ReactionStatus] = Field(default=None, serialization_alias="reactionStatus")

	feedback_ids: Optional[Collection[int]] = Field(
		default=None,
		serialization_alias=S11N_ALIAS_FEEDBACK_IDS,
		min_length=1,
		max_length=50,
	)

	@overload
	def __init__(
		self,
		*,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
		feedback_ids: Optional[Collection[int]] = None,
	) -> None: ...
	@overload
	def __init__(
		self,
		*,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
		datetime_from: Optional[Arrow] = None,
		datetime_to: Optional[Arrow] = None,
		paid: Optional[bool] = None,
		rating_values: Optional[Collection[int]] = None,
		reaction_status: Optional[ReactionStatus] = None,
	) -> None: ...
	def __init__(
		self,
		*,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
		feedback_ids: Optional[Collection[int]] = None,
		datetime_from: Optional[Arrow] = None,
		datetime_to: Optional[Arrow] = None,
		paid: Optional[bool] = None,
		rating_values: Optional[Collection[int]] = None,
		reaction_status: Optional[ReactionStatus] = None,
	) -> None:
		super().__init__(
			limit=limit,
			page_token=page_token,
			feedback_ids=feedback_ids,
			datetime_from=datetime_from,
			datetime_to=datetime_to,
			paid=paid,
			rating_values=rating_values,
			reaction_status=reaction_status,
		)

	@field_validator("limit", mode="after")
	@classmethod
	def limit_is_valid(cls, value: Optional[int]) -> Optional[int]:
		if value is None:
			return None

		if value < 1 or value > 50:
			raise ValueError("The limit cannot be less than 1 or greater than 50")

		return value

	@field_validator("rating_values", mode="after")
	@classmethod
	def rating_values_are_valid(cls, value: Optional[Collection[int]]) -> Optional[Collection[int]]:
		if value is None:
			return value

		for i in value:
			if i < 1 or i > 5:
				raise ValueError(f"{i} is not valid rating value. Must be in range [1..5]")

		return value

	@field_serializer("datetime_from", "datetime_to", mode="plain")
	def serialize_optional_arrow(self, value: Optional[Arrow]) -> Optional[str]:
		if value is None:
			return None

		return value.isoformat()

	@field_serializer("reaction_status", mode="plain")
	def serialize_reaction_status(self, value: Optional[ReactionStatus]) -> Optional[str]:
		if value is None:
			return None

		return value.value

	def model_dump_request_params(self) -> Dict[str, Any]:
		return self.model_dump(include=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

	def model_dump_request_payload(self) -> Dict[str, Any]:
		result = self.model_dump(exclude=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

		if self.feedback_ids is not None and len(result) != 1:
			warn("When using feedback_id, the other parameters will be ignored")
			result = {self.S11N_ALIAS_FEEDBACK_IDS: result[self.S11N_ALIAS_FEEDBACK_IDS]}

		return result


class FeedbackIdentifiers(BaseModel):
	model_id: Optional[int] = Field(default=None, validation_alias="modelId", deprecated=True)
	order_id: Optional[int] = Field(default=None, validation_alias="orderId")


class FeedbackStatistics(BaseModel):
	comments_count: int = Field(validation_alias="commentsCount")
	rating: int
	paid_amount: Optional[int] = Field(default=None, validation_alias="paidAmount")
	recommended: Optional[bool] = None


class FeedbackDescription(BaseModel):
	advantages: Optional[str] = None
	comment: Optional[str] = None
	disadvantages: Optional[str] = None


class FeedbackMedia(BaseModel):
	photos: List[str] = Field(default_factory=list)
	videos: List[str] = Field(default_factory=list)


class Feedback(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	id: int = Field(validation_alias="feedbackId")
	created_at: Arrow = Field(validation_alias="createdAt")
	identifiers: FeedbackIdentifiers
	need_reaction: bool = Field(validation_alias="needReaction")
	statistics: FeedbackStatistics
	author: Optional[str] = None
	description: Optional[FeedbackDescription] = None
	media: Optional[FeedbackMedia] = None

	@field_validator("created_at", mode="before")
	@classmethod
	def validate_arrow(cls, value: Any) -> Arrow:
		if not isinstance(value, str):
			raise ValueError("Raw value must be of str type")

		return get_arrow(value)


class Paging(BaseModel):
	next_page_token: Optional[str] = Field(default=None, validation_alias="nextPageToken")


class ResponseResult(BaseModel):
	feedbacks: List[Feedback]
	paging: Optional[Paging] = None


class Response(BaseResponse):
	result: Optional[ResponseResult] = None
