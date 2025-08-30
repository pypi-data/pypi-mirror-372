from typing import Optional
from datetime import time

from arrow import Arrow, get as get_arrow


def str_date_to_arrow(value: str, format: str = "DD-MM-YYYY") -> Arrow:
	return get_arrow(value, format)


def optional_str_date_to_optional_arrow(value: Optional[str], format: str = "DD-MM-YYYY") -> Optional[Arrow]:
	if value is None:
		return None

	return str_date_to_arrow(value, format)


def str_time_to_time(value: str) -> time:
	if not isinstance(value, str):
		raise ValueError("Time must be of string type")

	time_fragments = [int(i) for i in value.split(":")[:2]]

	if len(time_fragments) != 2:
		raise ValueError("Time must have hours and minutes")

	return time(hour=time_fragments[0], minute=time_fragments[1])


def optional_str_time_to_optional_time(value: Optional[str]) -> Optional[time]:
	if value is None:
		return None

	return str_time_to_time(value)


def str_datetime_to_arrow(value: str, format: str = "DD-MM-YYYY hh:mm:ss", tzinfo: str = "Europe/Moscow") -> Arrow:
	return get_arrow(value, format, tzinfo=tzinfo)


def optional_str_datetime_to_optional_arrow(
	value: Optional[str],
	format: str = "DD-MM-YYYY hh:mm:ss",
	tzinfo: str = "Europe/Moscow",
) -> Optional[Arrow]:
	if value is None:
		return None

	return str_datetime_to_arrow(value, format, tzinfo)
