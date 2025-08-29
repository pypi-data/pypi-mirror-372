from ya_market_api.base.enum_toolkit import allow_unknown

from enum import Enum


def test_allow_unknown():
	@allow_unknown
	class A(Enum):
		pass

	assert A.UNKNOWN.value == "UNKNOWN"		# type: ignore - Only for testing
	assert A("A") is A.UNKNOWN		# type: ignore - Only for testing

	@allow_unknown
	class B(Enum):
		A = "A"
		B = "B"
		UNKNOWN = "C"

	assert B.A.value == "A"
	assert B.B.value == "B"
	assert B.UNKNOWN.value == "C"
	assert B("A") is B.A
	assert B("D") is B.UNKNOWN
	assert B("F").value == "C"
