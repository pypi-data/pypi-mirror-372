import fastapi
import limits.storage
import limits.strategies
import pydantic

from ai_app.auth import get_username_if_authenticated
from ai_app.utils import (
    HttpMethod,
    PydanticForbidExtra,
    are_rate_limits_hit,
    get_remote_address,
)


class CorsConfig(PydanticForbidExtra):
    allow_origins: list[str] = []
    allow_credentials: bool = False
    allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: list[str] = ["*"]
    allow_origin_regex: str | None = None


def get_user_key_for_rate_limits(request: fastapi.Request) -> str:
    key = get_username_if_authenticated(request) or get_remote_address(request)
    return key


class EndpointRateLimitConfig(PydanticForbidExtra):
    method: HttpMethod
    path: str
    limit: str

    @pydantic.model_validator(mode="after")
    def _validate(cls, self):
        """Check that limit field conforms to limits library format."""
        self.rate_limits
        return self

    @property
    def rate_limits(self) -> list[limits.RateLimitItem]:
        return limits.parse_many(self.limit)

    def should_apply_limit(self, request: fastapi.Request) -> bool:
        return request.method == self.method and self.path in request.url.path

    def get_rate_limit_key(self, request: fastapi.Request) -> tuple[str, ...]:
        key = (self.method.value, self.path, get_user_key_for_rate_limits(request))
        return key


class RateLimitConfig(PydanticForbidExtra):
    storage_uri: str = "memory://"
    endpoint_limits: list[EndpointRateLimitConfig] = []

    def are_rate_limits_hit(
        self, request: fastapi.Request, limiter: limits.strategies.RateLimiter
    ) -> bool:
        limits_with_keys = []
        for endpoint_limit in self.endpoint_limits:
            if endpoint_limit.should_apply_limit(request):
                key = endpoint_limit.get_rate_limit_key(request)
                for rate_limit in endpoint_limit.rate_limits:
                    limits_with_keys.append((rate_limit, key))

        hit = are_rate_limits_hit(limiter, limits_with_keys)
        return hit

    def build_limiter(self) -> limits.strategies.RateLimiter:
        storage = limits.storage.storage_from_string(self.storage_uri)
        limiter = limits.strategies.MovingWindowRateLimiter(storage)
        return limiter
