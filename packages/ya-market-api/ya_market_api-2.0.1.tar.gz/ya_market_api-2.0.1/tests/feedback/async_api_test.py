from tests.fake_async_session import FakeAsyncSession
from ya_market_api.feedback.async_api import AsyncFeedbackAPI
from ya_market_api.feedback.dataclass import (
	FeedbackListRequest, FeedbackCommentListRequest, FeedbackCommentAddRequest, FeedbackCommentUpdateRequest,
	FeedbackCommentDeleteRequest, FeedbackReactionSkipRequest,
)
from ya_market_api.base.async_config import AsyncConfig

from unittest.mock import patch, Mock

import pytest


class TestAsyncFeedbackAPI:
	@pytest.mark.asyncio()
	async def test_get_feedback_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackListRequest(limit=50, page_token="page-token", feedback_ids=(1, 2, 3))

		with patch("ya_market_api.feedback.async_api.FeedbackListResponse") as FeedbackListResponseMock:
			FeedbackListResponseMock.model_validate_json = Mock()
			FeedbackListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_list() == "DESERIALIZED DATA"
				FeedbackListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_list(1)
				assert session.last_call_json == {}
				assert session.last_call_params == {}

				assert await api.get_feedback_list(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_list(1)
				assert session.last_call_json == {"feedbackIds": (1, 2, 3)}
				assert session.last_call_params == {"limit": 50, "page_token": "page-token"}

	@pytest.mark.asyncio()
	async def test_get_feedback_comment_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackCommentListRequest(limit=50, page_token="page-token", comment_ids=(1, 2, 3))

		with patch("ya_market_api.feedback.async_api.FeedbackCommentListResponse") as FeedbackCommentListResponseMock:
			FeedbackCommentListResponseMock.model_validate_json = Mock()
			FeedbackCommentListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_comment_list(request) == "DESERIALIZED DATA"
				FeedbackCommentListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_comment_list(1)
				assert session.last_call_json == {"commentIds": (1, 2, 3)}
				assert session.last_call_params == {"limit": 50, "page_token": "page-token"}

	@pytest.mark.asyncio()
	async def test_add_feedback_comment(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackCommentAddRequest.create(512, "COMMENT", 1024)

		with patch("ya_market_api.feedback.async_api.FeedbackCommentAddResponse") as FeedbackCommentAddResponse:
			FeedbackCommentAddResponse.model_validate_json = Mock()
			FeedbackCommentAddResponse.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.add_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentAddResponse.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_comment_add(1)
				assert session.last_call_json == {"feedbackId": 512, "comment": {"parentId": 1024, "text": "COMMENT"}}

	@pytest.mark.asyncio()
	async def test_update_feedback_comment(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackCommentUpdateRequest.create(512, 1024, "COMMENT")

		with patch("ya_market_api.feedback.async_api.FeedbackCommentUpdateResponse") as FeedbackCommentUpdateResponse:
			FeedbackCommentUpdateResponse.model_validate_json = Mock()
			FeedbackCommentUpdateResponse.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.update_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentUpdateResponse.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_comment_update(1)
				assert session.last_call_json == {"feedbackId": 512, "comment": {"id": 1024, "text": "COMMENT"}}

	@pytest.mark.asyncio()
	async def test_delete_feedback_comment(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackCommentDeleteRequest(id=512)

		with patch("ya_market_api.feedback.async_api.FeedbackCommentDeleteResponse") as FeedbackCommentDeleteResponse:
			FeedbackCommentDeleteResponse.model_validate_json = Mock()
			FeedbackCommentDeleteResponse.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.delete_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentDeleteResponse.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_comment_delete(1)
				assert session.last_call_json == {"id": 512}

	@pytest.mark.asyncio()
	async def test_skip_feedback_reaction(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, "", business_id=1)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackReactionSkipRequest(feedback_ids=(1, 2, 3))

		with patch("ya_market_api.feedback.async_api.FeedbackReactionSkipResponse") as FeedbackReactionSkipResponse:
			FeedbackReactionSkipResponse.model_validate_json = Mock()
			FeedbackReactionSkipResponse.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.skip_feedback_reaction(request) == "DESERIALIZED DATA"
				FeedbackReactionSkipResponse.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == api.router.feedback_reaction_skip(1)
				assert session.last_call_json == {"feedbackIds": (1, 2, 3)}
