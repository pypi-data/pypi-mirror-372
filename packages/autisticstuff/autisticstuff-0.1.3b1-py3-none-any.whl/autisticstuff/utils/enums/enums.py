from enum import IntEnum, StrEnum

from starlette.status import (
	HTTP_400_BAD_REQUEST,
	HTTP_401_UNAUTHORIZED,
	HTTP_403_FORBIDDEN,
	HTTP_404_NOT_FOUND,
	HTTP_409_CONFLICT,
	HTTP_418_IM_A_TEAPOT,
	HTTP_422_UNPROCESSABLE_ENTITY,
	HTTP_500_INTERNAL_SERVER_ERROR,
	HTTP_501_NOT_IMPLEMENTED,
	HTTP_502_BAD_GATEWAY,
)


class APIErrorSpecs(StrEnum):
	unknown_error = "Unknown error"
	not_found = "Not found"
	validation_error = "Invalid body / query of a request / response"
	internal_server_error = "Internal server error"
	external_service_unavailible = "Could not fetch external service"
	database_error = "Error on a repository level"
	session_expired = "Unauthorized"
	insufficient_permissions = "Forbidden"
	banned = ":)))"
	unauthorized = "Unauthorized"
	unloaded_prop = "Missing greenlet"


class StatusCodeMap(IntEnum):
	unknown_error = HTTP_400_BAD_REQUEST
	not_found = HTTP_404_NOT_FOUND
	validation_error = HTTP_422_UNPROCESSABLE_ENTITY
	internal_server_error = HTTP_500_INTERNAL_SERVER_ERROR
	external_service_unavailible = HTTP_502_BAD_GATEWAY
	database_error = HTTP_409_CONFLICT
	insufficient_permissions = HTTP_403_FORBIDDEN
	session_expired = HTTP_401_UNAUTHORIZED
	banned = HTTP_418_IM_A_TEAPOT
	unauthorized = HTTP_401_UNAUTHORIZED
	unloaded_prop = HTTP_501_NOT_IMPLEMENTED
