from ya_market_api.base.convert import (
	str_date_to_arrow, optional_str_date_to_optional_arrow, str_time_to_time, optional_str_time_to_optional_time,
	str_datetime_to_arrow, optional_str_datetime_to_optional_arrow,
)

from datetime import time

import pytest
from arrow import get as get_arrow


def test_str_date_to_arrow():
	assert str_date_to_arrow("31-12-2025") == get_arrow(2025, 12, 31)
	assert str_date_to_arrow("2025-12-31", "YYYY-MM-DD") == get_arrow(2025, 12, 31)


def test_optional_str_date_to_optional_arrow():
	assert optional_str_date_to_optional_arrow(None) is None
	assert optional_str_date_to_optional_arrow(None, "YYYY-MM-DD") is None
	assert optional_str_date_to_optional_arrow("31-12-2025") == get_arrow(2025, 12, 31)
	assert optional_str_date_to_optional_arrow("2025-12-31", "YYYY-MM-DD") == get_arrow(2025, 12, 31)


def test_str_time_to_time():
	assert str_time_to_time("12:30") == time(hour=12, minute=30)
	assert str_time_to_time("12:30:15") == time(hour=12, minute=30)

	with pytest.raises(ValueError, match="Time must be of string type"):
		str_time_to_time(None)		# type: ignore

	with pytest.raises(ValueError, match="Time must have hours and minutes"):
		str_time_to_time("12")		# type: ignore


def test_optional_str_time_to_optional_time():
	assert optional_str_time_to_optional_time(None) is None
	assert optional_str_time_to_optional_time("12:30") == time(hour=12, minute=30)


def test_str_datetime_to_arrow():
	assert str_datetime_to_arrow("31-12-2025 12:30:15") == get_arrow(2025, 12, 31, 12, 30, 15, tzinfo="Europe/Moscow")
	assert (
		str_datetime_to_arrow(
			"2025-12-31T12:30:15",
			"YYYY-MM-DDThh:mm:ss",
		) == get_arrow(
			2025, 12, 31, 12, 30, 15, tzinfo="Europe/Moscow",
		)
	)
	assert (
		str_datetime_to_arrow(
			"2025-12-31T12:30:15",
			"YYYY-MM-DDThh:mm:ss",
			"Asia/Hong_Kong",
		) == get_arrow(
			2025, 12, 31, 12, 30, 15, tzinfo="Asia/Hong_Kong",
		)
	)


def test_optional_str_datetime_to_optional_arrow():
	assert optional_str_datetime_to_optional_arrow(None) is None
	assert (
		optional_str_datetime_to_optional_arrow(
			"31-12-2025 12:30:15"
		) == get_arrow(
			2025, 12, 31, 12, 30, 15, tzinfo="Europe/Moscow",
		)
	)
	assert (
		optional_str_datetime_to_optional_arrow(
			"2025-12-31T12:30:15",
			"YYYY-MM-DDThh:mm:ss",
		) == get_arrow(
			2025, 12, 31, 12, 30, 15, tzinfo="Europe/Moscow",
		)
	)
	assert (
		optional_str_datetime_to_optional_arrow(
			"2025-12-31T12:30:15",
			"YYYY-MM-DDThh:mm:ss",
			"Asia/Hong_Kong",
		) == get_arrow(
			2025, 12, 31, 12, 30, 15, tzinfo="Asia/Hong_Kong",
		)
	)
