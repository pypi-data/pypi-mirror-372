from ya_market_api.base.enum_toolkit import allow_unknown

from enum import Enum


@allow_unknown
class APIAvailabilityStatus(Enum):
	AVAILABLE = "AVAILABLE"
	DISABLED_BY_INACTIVITY = "DISABLED_BY_INACTIVITY"


@allow_unknown
class PlacementType(Enum):
	FBS = "FBS"
	FBY = "FBY"
	DBS = "DBS"
