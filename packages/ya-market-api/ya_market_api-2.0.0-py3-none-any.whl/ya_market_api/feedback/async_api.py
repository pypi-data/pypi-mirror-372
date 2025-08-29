from ya_market_api.base.async_api_mixin import AsyncAPIMixin
from ya_market_api.feedback.base_api import BaseFeedbackAPI
from ya_market_api.feedback.dataclass import (
	FeedbackListRequest, FeedbackListResponse, FeedbackCommentListRequest, FeedbackCommentListResponse,
	FeedbackCommentAddRequest, FeedbackCommentAddResponse, FeedbackCommentUpdateRequest, FeedbackCommentUpdateResponse,
	FeedbackCommentDeleteRequest, FeedbackCommentDeleteResponse, FeedbackReactionSkipRequest,
	FeedbackReactionSkipResponse,
)

from typing import Optional


class AsyncFeedbackAPI(AsyncAPIMixin, BaseFeedbackAPI):
	async def get_feedback_list(self, request: Optional[FeedbackListRequest] = None) -> FeedbackListResponse:
		request = request or FeedbackListRequest()
		url = self.router.feedback_list(self.business_id)

		async with self.session.post(
			url=url,
			params=request.model_dump_request_params(),
			json=request.model_dump_request_payload(),
		) as response:
			self.validate_response(response)
			return FeedbackListResponse.model_validate_json(await response.text())

	async def get_feedback_comment_list(self, request: FeedbackCommentListRequest) -> FeedbackCommentListResponse:
		url = self.router.feedback_comment_list(self.business_id)

		async with self.session.post(
			url=url,
			params=request.model_dump_request_params(),
			json=request.model_dump_request_payload(),
		) as response:
			self.validate_response(response)
			return FeedbackCommentListResponse.model_validate_json(await response.text())

	async def add_feedback_comment(self, request: FeedbackCommentAddRequest) -> FeedbackCommentAddResponse:
		url = self.router.feedback_comment_add(self.business_id)

		async with self.session.post(
			url=url,
			json=request.model_dump(by_alias=True, exclude_defaults=True),
		) as response:
			self.validate_response(response)
			return FeedbackCommentAddResponse.model_validate_json(await response.text())

	async def update_feedback_comment(self, request: FeedbackCommentUpdateRequest) -> FeedbackCommentUpdateResponse:
		url = self.router.feedback_comment_update(self.business_id)

		async with self.session.post(
			url=url,
			json=request.model_dump(by_alias=True, exclude_defaults=True),
		) as response:
			self.validate_response(response)
			return FeedbackCommentUpdateResponse.model_validate_json(await response.text())

	async def delete_feedback_comment(self, request: FeedbackCommentDeleteRequest) -> FeedbackCommentDeleteResponse:
		url = self.router.feedback_comment_delete(self.business_id)

		async with self.session.post(url, json=request.model_dump(by_alias=True, exclude_defaults=True)) as response:
			self.validate_response(response)
			return FeedbackCommentDeleteResponse.model_validate_json(await response.text())

	async def skip_feedback_reaction(self, request: FeedbackReactionSkipRequest) -> FeedbackReactionSkipResponse:
		url = self.router.feedback_reaction_skip(self.business_id)

		async with self.session.post(url, json=request.model_dump(by_alias=True, exclude_defaults=True)) as response:
			self.validate_response(response)
			return FeedbackReactionSkipResponse.model_validate_json(await response.text())
