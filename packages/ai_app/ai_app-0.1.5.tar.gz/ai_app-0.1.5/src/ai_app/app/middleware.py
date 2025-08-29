import logging

import fastapi.middleware.cors
import fastapi.responses
import starlette.middleware.base
import starlette.middleware.sessions
import starlette.types

from ai_app.config import RateLimitConfig, get_config
from ai_app.utils import is_redirect_response


def add_middleware(app: fastapi.FastAPI):
    """
    Order of middleware matters - order of dispatch calls is reverse to the order of middleware addition.
    So the last added middleware is first to see the request and last to see the response.
    """
    app.add_middleware(
        RateLimitsMiddleware,
        rate_limit_config=get_config().rate_limit_config,
    )
    app.add_middleware(
        starlette.middleware.sessions.SessionMiddleware,
        secret_key=get_config().secrets.session_crypto_key.get_secret_value(),
    )
    app.add_middleware(BlockGradioFileEndpointRedirectsMiddleware)
    app.add_middleware(
        SecurityHeadersMiddleware,
        security_headers=get_config().security_headers,
    )
    app.add_middleware(RemoveGradioCorsHeadersMiddleware)
    app.add_middleware(
        fastapi.middleware.cors.CORSMiddleware,
        **get_config().cors_config.model_dump(),
    )
    if get_config().is_prod:
        app.add_middleware(SanitizeInternalErrorResponsesMiddleware)


def try_log_response_body_as_error(response: fastapi.Response):
    try:
        body = response.body
        body = body.tobytes() if isinstance(body, memoryview) else body
        body = body.decode()
        logging.error(f"Internal server error: {body}")
    except Exception as e:
        logging.error(f"Error processing error response: {e}")


def get_generic_500_error_response() -> fastapi.responses.JSONResponse:
    generic_500_error_response = fastapi.responses.JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    return generic_500_error_response


def get_generic_429_error_response() -> fastapi.responses.JSONResponse:
    generic_429_error_response = fastapi.responses.JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )
    return generic_429_error_response


class SanitizeInternalErrorResponsesMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next) -> fastapi.Response:
        try:
            response = await call_next(request)
        except Exception as e:
            logging.error(f"Error when processing request: {e}")
            response = get_generic_500_error_response()
        else:
            if response.status_code >= 500:
                response = get_generic_500_error_response()
                try_log_response_body_as_error(response)

        return response


class BlockGradioFileEndpointRedirectsMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next) -> fastapi.Response:
        response = await call_next(request)
        if is_redirect_response(response) and "/gradio_api/file=" in request.url.path:
            response = fastapi.Response(
                status_code=400,
                content="Redirects are not allowed for Gradio file endpoint",
            )

        return response


class RemoveGradioCorsHeadersMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    """
    Removes Gradio CORS headers from the response, as they may be too permissive.
    For enhanced safety, the headers in the response should be properly set after this middleware.
    """

    async def dispatch(self, request: fastapi.Request, call_next) -> fastapi.Response:
        response = await call_next(request)
        del response.headers["Access-Control-Allow-Origin"]
        del response.headers["Access-Control-Allow-Credentials"]
        return response


class SecurityHeadersMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    def __init__(self, app: starlette.types.ASGIApp, security_headers: dict[str, str]):
        """The app argument is the FastAPI app or the previous middleware instance in the chain."""
        super().__init__(app)
        self.security_headers = security_headers

    async def dispatch(self, request: fastapi.Request, call_next) -> fastapi.Response:
        response = await call_next(request)
        response.headers.update(self.security_headers)
        return response


class RateLimitsMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    """
    A SessionMiddleware should be added after this middleware
    if the rate limit key depends on the session.
    """

    def __init__(self, app: starlette.types.ASGIApp, rate_limit_config: RateLimitConfig):
        super().__init__(app)
        self.limiter = rate_limit_config.build_limiter()
        self.rate_limit_config = rate_limit_config

    async def dispatch(self, request: fastapi.Request, call_next):
        if self.rate_limit_config.are_rate_limits_hit(request, self.limiter):
            response = get_generic_429_error_response()
        else:
            response = await call_next(request)

        return response
