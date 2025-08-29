from ya_market_api.feedback.sync_api import SyncFeedbackAPI
from ya_market_api.feedback.dataclass import (
	FeedbackListRequest, FeedbackCommentListRequest, FeedbackCommentAddRequest, FeedbackCommentUpdateRequest,
	FeedbackCommentDeleteRequest, FeedbackReactionSkipRequest,
)
from ya_market_api.base.sync_config import SyncConfig

from unittest.mock import patch, Mock


class TestSyncFeedbackAPI:
	def test_get_feedback_list(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackListRequest(limit=50, page_token="page-token", feedback_ids=(1, 2, 3))

		with patch("ya_market_api.feedback.sync_api.FeedbackListResponse") as FeedbackListResponseMock:
			FeedbackListResponseMock.model_validate_json = Mock()
			FeedbackListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_list() == "DESERIALIZED DATA"
				FeedbackListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(url=api.router.feedback_list(1), params={}, json={})

				session.post.reset_mock()
				assert api.get_feedback_list(request) == "DESERIALIZED DATA"
				session.post.assert_called_once_with(
					url=api.router.feedback_list(1),
					params={"limit": 50, "page_token": "page-token"},
					json={"feedbackIds": (1, 2, 3)},
				)

	def test_get_feedback_comment_list(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackCommentListRequest(comment_ids=(1, 2, 3), limit=50, page_token="page-token")

		with patch("ya_market_api.feedback.sync_api.FeedbackCommentListResponse") as FeedbackCommentListResponseMock:
			FeedbackCommentListResponseMock.model_validate_json = Mock()
			FeedbackCommentListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_comment_list(request) == "DESERIALIZED DATA"
				FeedbackCommentListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					url=api.router.feedback_comment_list(1),
					params={"limit": 50, "page_token": "page-token"},
					json={"commentIds": (1, 2, 3)},
				)

	def test_add_feedback_comment(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackCommentAddRequest.create(512, "COMMENT", 1024)

		with patch("ya_market_api.feedback.sync_api.FeedbackCommentAddResponse") as FeedbackCommentAddResponseMock:
			FeedbackCommentAddResponseMock.model_validate_json = Mock()
			FeedbackCommentAddResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.add_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentAddResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					url=api.router.feedback_comment_add(1),
					json={"feedbackId": 512, "comment": {"parentId": 1024, "text": "COMMENT"}},
				)

	def test_update_feedback_comment(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackCommentUpdateRequest.create(512, 1024, "COMMENT")

		with patch("ya_market_api.feedback.sync_api.FeedbackCommentUpdateResponse") as FeedbackCommentUpdateResponseMock:
			FeedbackCommentUpdateResponseMock.model_validate_json = Mock()
			FeedbackCommentUpdateResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.update_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentUpdateResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					url=api.router.feedback_comment_update(1),
					json={"feedbackId": 512, "comment": {"id": 1024, "text": "COMMENT"}},
				)

	def test_delete_feedback_comment(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackCommentDeleteRequest(id=512)

		with patch("ya_market_api.feedback.sync_api.FeedbackCommentDeleteResponse") as FeedbackCommentDeleteResponseMock:
			FeedbackCommentDeleteResponseMock.model_validate_json = Mock()
			FeedbackCommentDeleteResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.delete_feedback_comment(request) == "DESERIALIZED DATA"
				FeedbackCommentDeleteResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					url=api.router.feedback_comment_delete(1),
					json={"id": 512},
				)

	def test_skip_feedback_reaction(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, "", business_id=1)
		api = SyncFeedbackAPI(config)
		request = FeedbackReactionSkipRequest(feedback_ids=(1, 2, 3))

		with patch("ya_market_api.feedback.sync_api.FeedbackReactionSkipResponse") as FeedbackReactionSkipResponseMock:
			FeedbackReactionSkipResponseMock.model_validate_json = Mock()
			FeedbackReactionSkipResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.skip_feedback_reaction(request) == "DESERIALIZED DATA"
				FeedbackReactionSkipResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					url=api.router.feedback_reaction_skip(1),
					json={"feedbackIds": (1, 2, 3)},
				)
