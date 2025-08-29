from enum import Enum
from typing import Type, Any, TypeVar


T = TypeVar("T", bound=Type[Enum])


def allow_unknown(cls: T) -> T:
	"""
	Extends existing enumeration, which allows it to interpret all unspecified values as UNKNOWN.

	Examples:
		>>> from enum import Enum
		>>> @allow_unknown
		>>> class A(Enum):
		>>> 	A = "A"
		>>> print(A("A"))		# "A.A"
		>>> print(A("B"))		# "A.UNKNOWN"
		>>> print(A.UNKNOWN)		# "A.UNKNOWN"
		>>> print(A.A)		# "A.UNKNOWN"

	Notes:
		* Static code checkers don't know about the "UNKNOWN" option and won't let you use it.
	"""
	values = {"UNKNOWN": "UNKNOWN"}

	for i in cls:
		values[i.name] = i.value


	class MissingProxy(Enum):
		@classmethod
		def _missing_(cls, value: Any):
			return cls.UNKNOWN


	return Enum(cls.__name__, values, type=MissingProxy)
