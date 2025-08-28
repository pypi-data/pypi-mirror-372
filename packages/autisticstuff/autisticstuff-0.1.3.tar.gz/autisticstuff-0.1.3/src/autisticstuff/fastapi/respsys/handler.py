from collections.abc import Callable
from contextlib import suppress

import fastapi
from fastapi.requests import Request
import starlette
from starlette.status import HTTP_401_UNAUTHORIZED

from autisticstuff.logs import get_logger
from autisticstuff.utils.enums import APIErrorSpecs, StatusCodeMap

from .exceptions import APIException
from .schemas.response import ErrorSO, ResponseSO


def _ph_delete_auth_cookie(_):
	get_logger("exchandler").critical("DELETE AUTH COOKIE METHOD IS UNIMPLEMENTED!")


async def exception_handler(request: Request, exception: Exception) -> starlette.responses.JSONResponse:
	status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR

	if isinstance(exception, APIException):
		error = exception.error_so
		status_code = exception.status_code
	else:
		error = ErrorSO(
			spec=APIErrorSpecs.unknown_error,
			detail="unknown error emitted; contact @plastictactic with data below",
			context={
				"exception_type": str(type(exception)),
				"exception_str": str(exception),
				"request.method": str(request.method),
				"request.url": str(request.url),
			},
		)

		if isinstance(exception, starlette.exceptions.HTTPException):
			status_code = (
				exception.status_code
				if exception.status_code in StatusCodeMap
				else fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
			)

			with suppress(Exception):
				error.context["exception.detail"] = exception.detail

		elif isinstance(exception, fastapi.exceptions.RequestValidationError):
			status_code = fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

			with suppress(Exception):
				error.context["exception.errors"] = str(exception.errors()) if exception.errors() else {}
		else:
			status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR

		error.spec = StatusCodeMap(status_code).name
		error.detail = APIErrorSpecs[error.spec]

	error.context["status_code"] = status_code

	response = starlette.responses.JSONResponse(
		content=ResponseSO(payload=None, error=error).model_dump(mode="json", fallback=str),
		status_code=status_code,
	)
	if status_code == HTTP_401_UNAUTHORIZED:
		"""
		Call the delete cookie function attached to the app state (fallback to placeholder).
		"""

		with suppress(Exception):
			delete_cookie_func = getattr(request.app.state, "delete_cookie_func", _ph_delete_auth_cookie)
			delete_cookie_func(response)

	return response


def apply_exception_handler(
	app: fastapi.FastAPI, delete_cookie_func: Callable[[fastapi.Response], None] = _ph_delete_auth_cookie
):
	app.state.delete_cookie_func = delete_cookie_func

	app.add_exception_handler(exc_class_or_status_code=Exception, handler=exception_handler)

	app.add_exception_handler(exc_class_or_status_code=APIException, handler=exception_handler)

	app.add_exception_handler(
		exc_class_or_status_code=fastapi.exceptions.WebSocketRequestValidationError,
		handler=exception_handler,
	)

	app.add_exception_handler(
		exc_class_or_status_code=starlette.exceptions.HTTPException,
		handler=exception_handler,
	)

	app.add_exception_handler(
		exc_class_or_status_code=fastapi.exceptions.RequestValidationError,
		handler=exception_handler,
	)
