import httpx

from ai_app.utils import build_url_with_parameters, join_url


def get_openid_metadata_url(base_url: str) -> str:
    """Common OpenID metadata URL for auth providers."""
    url = join_url(base_url, "/.well-known/openid-configuration")
    return url


def get_keycloak_realm_url(base_url: str, realm: str) -> str:
    """Keycloak realm URL."""
    url = join_url(base_url, "realms", realm)
    return url


def to_absolute_route(route: str) -> str:
    route = "/" + route.strip("/")
    return route


def get_minimal_openid_scope() -> str:
    return "email openid profile"


def get_openid_metadata(base_url: str, **kwargs) -> dict:
    response = httpx.get(get_openid_metadata_url(base_url), **kwargs)
    response.raise_for_status()
    metadata = response.json()
    return metadata


def build_logout_redirect_url(
    end_session_endpoint: str, post_logout_redirect_uri: str, id_token: str | None = None
) -> str:
    logout_params = {
        "post_logout_redirect_uri": post_logout_redirect_uri,
    }
    # id_token_hint is recommended by OIDC spec for logout
    if id_token:
        logout_params["id_token_hint"] = id_token

    logout_url = build_url_with_parameters(end_session_endpoint, **logout_params)
    return logout_url
