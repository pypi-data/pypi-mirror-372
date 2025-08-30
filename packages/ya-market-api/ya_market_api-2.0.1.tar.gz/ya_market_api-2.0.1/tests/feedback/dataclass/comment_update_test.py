from ya_market_api.feedback.dataclass.comment_update import Request, RequestComment


class TestRequest:
	def test_create(self):
		request = Request.create(512, 1024, "comment-text")
		assert isinstance(request, Request)
		assert isinstance(request.comment, RequestComment)
		assert request.feedback_id == 512
		assert request.comment.id == 1024
		assert request.comment.text == "comment-text"
