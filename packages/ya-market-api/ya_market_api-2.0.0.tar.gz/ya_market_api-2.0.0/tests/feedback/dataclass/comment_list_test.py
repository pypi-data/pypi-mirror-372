from ya_market_api.feedback.dataclass.comment_list import Request

import pytest


class TestRequest:
	def test___init__(self):
		request = Request(comment_ids=(1, 2, 3))
		assert request.comment_ids == (1, 2, 3)

		request = Request(feedback_id=1)
		assert request.feedback_id == 1

	def test_model_dump_request_params(self):
		request = Request(comment_ids=(1, 2, 3))
		assert request.model_dump_request_params() == {}

		request = Request(comment_ids=(1, 2, 3), limit=100, page_token="page-token")
		assert request.model_dump_request_params() == {"limit": 100, "page_token": "page-token"}

	def test_model_dump_request_payload(self):
		request = Request(comment_ids=(1, 2, 3))
		request.feedback_id = 1

		with pytest.warns(UserWarning, match="When using comment_ids, the other parameters will be ignored"):
			assert request.model_dump_request_payload() == {request.S11N_ALIAS_COMMENT_IDS: (1, 2, 3)}

		request.comment_ids = None
		request.feedback_id = None

		with pytest.raises(ValueError, match="feedback_id or comment_ids are required"):
			request.model_dump_request_payload()

		request.comment_ids = (1, 2, 3)
		request.limit = 100
		request.page_token = "page-token"
		assert request.model_dump_request_payload() == {request.S11N_ALIAS_COMMENT_IDS: (1, 2, 3)}
