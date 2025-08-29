class APIError(Exception):
	"""
	Base API error class.
	"""
	pass


class InvalidResponseError(APIError):
	pass


class AuthorizationError(InvalidResponseError):
	pass


class NotFoundError(InvalidResponseError):
	pass


class BusinessIdError(APIError):
	pass


class CampaignIdError(APIError):
	pass
