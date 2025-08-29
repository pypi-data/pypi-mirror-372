from typing import Any, ClassVar

import fastapi

from autisticstuff.utils.enums import APIErrorSpecs, StatusCodeMap

from ..schemas.response import ErrorSO


class APIException(fastapi.exceptions.HTTPException):
	specs: ClassVar[APIErrorSpecs] = APIErrorSpecs.unknown_error

	def __init__(self, *, detail: str | None = None, context: dict[str, Any] | None = None):
		self.status_code = StatusCodeMap[self.specs.name]

		self.error = self.specs.value
		self.detail = detail
		self.context = context if context is not None else {}

		self.error_so = ErrorSO(spec=self.error, detail=self.detail, context=self.context)

		super().__init__(status_code=self.status_code, detail=self.error_so.model_dump(mode="json"))


class BannedError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.banned


class NotFoundError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.not_found


class ValidationError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.validation_error


class DatabaseError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.database_error


class ExternalServiceError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.external_service_unavailible


class InternalServerError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.internal_server_error


class UnauthorizedError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.unauthorized


class ForbiddenError(APIException):
	specs: APIErrorSpecs = APIErrorSpecs.insufficient_permissions


__all__ = [
	"APIException",
	"BannedError",
	"DatabaseError",
	"ExternalServiceError",
	"ForbiddenError",
	"InternalServerError",
	"NotFoundError",
	"UnauthorizedError",
	"ValidationError",
]
