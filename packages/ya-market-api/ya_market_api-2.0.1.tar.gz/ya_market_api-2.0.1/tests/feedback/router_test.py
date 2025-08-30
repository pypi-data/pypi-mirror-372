from ya_market_api.feedback.router import FeedbackRouter


class TestFeedbackRouter:
	def test_feedback_list(self):
		router = FeedbackRouter("")
		assert router.feedback_list(512) == "/businesses/512/goods-feedback"

	def test_feedback_comment_list(self):
		router = FeedbackRouter("")
		assert router.feedback_comment_list(512) == "/businesses/512/goods-feedback/comments"

	def test_feedback_comment_add(self):
		router = FeedbackRouter("")
		assert router.feedback_comment_add(512) == "/businesses/512/goods-feedback/comments/update"

	def test_feedback_comment_update(self):
		router = FeedbackRouter("")
		assert router.feedback_comment_update(512) == "/businesses/512/goods-feedback/comments/update"

	def test_feedback_comment_delete(self):
		router = FeedbackRouter("")
		assert router.feedback_comment_delete(512) == "/businesses/512/goods-feedback/comments/delete"

	def test_feedback_reaction_skip(self):
		router = FeedbackRouter("")
		assert router.feedback_reaction_skip(512) == "/businesses/512/goods-feedback/skip-reaction"
