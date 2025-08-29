from ya_market_api.feedback.dataclass.list import Request, Feedback
from ya_market_api.feedback.const import ReactionStatus

import pytest
from arrow import get


class TestRequest:
	def test___init__(self):
		request = Request(feedback_ids=(1, 2, 3), limit=25, page_token="page-token")
		assert request.feedback_ids == (1, 2, 3)
		assert request.limit == 25
		assert request.page_token == "page-token"

		request = Request(datetime_from=get(2025, 1, 1), datetime_to=get(2025, 2, 1))
		assert request.datetime_from == get(2025, 1, 1)
		assert request.datetime_to == get(2025, 2, 1)

	def test_limit_is_valid(self):
		assert Request.limit_is_valid(None) is None
		assert Request.limit_is_valid(25) == 25

		with pytest.raises(ValueError, match="The limit cannot be less than 1 or greater than 50"):
			Request.limit_is_valid(0)

		with pytest.raises(ValueError, match="The limit cannot be less than 1 or greater than 50"):
			Request.limit_is_valid(51)

	def test_rating_values_are_valid(self):
		assert Request.rating_values_are_valid(None) is None
		assert Request.rating_values_are_valid([]) == []
		assert Request.rating_values_are_valid([1, 2, 3]) == [1, 2, 3]

		with pytest.raises(ValueError, match=r"0 is not valid rating value. Must be in range \[1\.\.5\]"):
			assert Request.rating_values_are_valid([3, 2, 1, 0])

		with pytest.raises(ValueError, match=r"6 is not valid rating value. Must be in range \[1\.\.5\]"):
			assert Request.rating_values_are_valid([4, 5, 6])

	def test_serialize_optional_arrow(self):
		request = Request(feedback_ids=[1])

		assert request.serialize_optional_arrow(None) is None
		assert request.serialize_optional_arrow(get(2025, 1, 1, 12, 30, 30)) == "2025-01-01T12:30:30+00:00"

	def test_serialize_reaction_status(self):
		request = Request(feedback_ids=[1])

		assert request.serialize_reaction_status(None) is None
		assert request.serialize_reaction_status(ReactionStatus.ALL) == ReactionStatus.ALL.value

	def test_model_dump_request_params(self):
		request = Request(feedback_ids=[1, 2, 3], limit=50, page_token="page-token")
		assert request.model_dump_request_params() == {"limit": 50, "page_token": "page-token"}

	def test_model_dump_request_payload(self):
		request = Request(feedback_ids=[1, 2, 3], limit=50, page_token="page-token")
		assert request.model_dump_request_payload() == {"feedbackIds": [1, 2, 3]}

		request = Request(datetime_from=get(2025, 1, 1, 12, 30, 30), datetime_to=get(2025, 2, 1))
		assert request.model_dump_request_payload() == {
			"dateTimeFrom": "2025-01-01T12:30:30+00:00",
			"dateTimeTo": "2025-02-01T00:00:00+00:00",
		}

		request.feedback_ids = [1, 2, 3]

		with pytest.warns(UserWarning, match="When using feedback_id, the other parameters will be ignored"):
			assert request.model_dump_request_payload() == {"feedbackIds": [1, 2, 3]}


class TestFeedback:
	def test_validate_arrow(self):
		assert Feedback.validate_arrow("2025-01-01T12:30:30.500+03:00") == get(2025, 1, 1, 12, 30, 30, 500000, tzinfo="Europe/Moscow")

		with pytest.raises(ValueError, match="Raw value must be of str type"):
			Feedback.validate_arrow(5)
