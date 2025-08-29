from ya_market_api.feedback.dataclass.comment_add import Request, RequestComment


class TestRequest:
	def test_create(self):
		request = Request.create(512, "comment-text")
		assert isinstance(request, Request)
		assert isinstance(request.comment, RequestComment)
		assert request.feedback_id == 512
		assert request.comment.text == "comment-text"
		assert request.comment.parent_id is None

		request = Request.create(512, "comment-text", parent_id=1024)
		assert request.feedback_id == 512
		assert request.comment.text == "comment-text"
		assert request.comment.parent_id == 1024
