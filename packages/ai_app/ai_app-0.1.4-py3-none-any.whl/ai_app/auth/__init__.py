import logging
import time
import urllib
import webbrowser
from typing import Iterable

import authlib.integrations.httpx_client
import authlib.integrations.starlette_client
import fastapi
import gradio as gr
import starlette.middleware.sessions
import starlette.responses

from ai_app.auth.utils import (
    build_logout_redirect_url,
    get_minimal_openid_scope,
    get_openid_metadata,
    get_openid_metadata_url,
    to_absolute_route,
)
from ai_app.utils import build_url_with_parameters, compress, decompress, filter_dict_by_keys


class OAuth:
    oauth_registry: authlib.integrations.starlette_client.OAuth
    starlette_client: authlib.integrations.starlette_client.StarletteOAuth2App
    httpx_client: authlib.integrations.httpx_client.OAuth2Client
    openid_metadata: dict[str, str]

    def __init__(
        self,
        provider_base_url: str,
        client_id: str,
        client_secret: str,
        scope: str | None = None,
        oauth: authlib.integrations.starlette_client.OAuth | None = None,
        provider_name: str = "oauth_provider",
        redirect_uri: str = "http://localhost/auth",
    ):
        scope = scope or get_minimal_openid_scope()
        self.oauth_registry = oauth or authlib.integrations.starlette_client.OAuth()
        self.oauth_registry.register(
            name=provider_name,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=get_openid_metadata_url(provider_base_url),
            client_kwargs={"scope": scope, "verify": False},
        )

        self.starlette_client = self.oauth_registry.create_client(provider_name)
        self.httpx_client = authlib.integrations.httpx_client.AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            redirect_uri=redirect_uri,
        )
        self.openid_metadata = get_openid_metadata(provider_base_url)

    def interactive_authorization(self) -> tuple[dict, dict]:
        """
        Manually open the authorization URL in the browser, login, and copy the resulting
        redirected URL into the parse_redirected_url method.
        Meant only for testing in interactive environments.
        """
        authorization_url, auth_state = self.httpx_client.create_authorization_url(
            self.openid_metadata["authorization_endpoint"]
        )
        webbrowser.open(authorization_url)
        redirected_url = input("Paste the full redirect URL here: ")
        parsed_url = urllib.parse.urlparse(redirected_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        authorization_code = query_params.get("code", [None])[0]
        returned_state = query_params.get("state", [None])[0]
        if auth_state != returned_state:
            raise ValueError("State mismatch. Possible CSRF attack.")

        token = self.httpx_client.fetch_token(
            self.openid_metadata["token_endpoint"],
            code=authorization_code,
        )

        response = self.httpx_client.get(self.openid_metadata["userinfo_endpoint"])
        response.raise_for_status()
        userinfo = response.json()
        return token, userinfo


def get_username_if_authenticated(request: fastapi.Request) -> str | None:
    """
    Returns None if user is not authenticated, otherwise returns the user name,
    which had to be manually saved in the session upon user login.
    Can be directly passed to the Gradio mount_gradio_app method as an auth dependency.
    https://www.gradio.app/docs/gradio/mount_gradio_app#param-mount_gradio_app-auth-dependency
    """
    expires_at = request.session.get("access_token_expires_at")
    user_info = request.session.get("user_info")
    if not user_info or expires_at and expires_at < time.time():
        return

    username = user_info.get("name")
    return username


def check_oauth_error_in_url_params(request: gr.Request):
    error = request.query_params.get("error")
    if error:
        description = request.query_params.get("description")
        raise gr.Error(f"OAuth failed with error: '{error}' and description: '{description}'")


def mount_auth_for_gradio_app(
    oauth_client: authlib.integrations.starlette_client.StarletteOAuth2App,
    gradio_app: gr.Blocks,
    login_gradio_app: gr.Blocks | None = None,
    gradio_app_route: str = "gradio",
    login_gradio_app_route: str = "gradio-login",
    auth_redirect_route: str = "auth",
    app: fastapi.FastAPI | None = None,
    session_crypto_key: str | None = None,
    end_session_endpoint: str | None = None,
    userinfo_fields: Iterable[str] = ("employeeID", "preferred_username", "name", "email"),
    max_id_token_size: int = 0,
    login_gradio_app_kwargs: dict | None = None,
    gradio_app_kwargs: dict | None = None,
) -> fastapi.FastAPI:
    """
    The auth_redirect_path should be the one registered by the client with the OAuth provider.
    The max_id_token_size parameter sets the maximum size of the id_token to be saved in the session.
    If it's too big, the whole session cookie will be dropped, disabling login.
    The id_token is only needed for proper logout handling, so it is not crucial to save it if it's too big.
    Usually the session cookie size is about 4KB, so only necessary data should be stored in it.

    If browser sessions are encoded with different crypto keys, they will not be reused,
    so it's better to persist the key between app restarts.
    A secure key can be generated with secrets.token_hex(32).
    """
    # Todo: move id_token to a server-side session storage, like Redis.
    gradio_app_route = to_absolute_route(gradio_app_route)
    login_gradio_app_route = to_absolute_route(login_gradio_app_route)
    auth_redirect_route = to_absolute_route(auth_redirect_route)
    app = app or fastapi.FastAPI()
    if session_crypto_key:
        app.add_middleware(
            starlette.middleware.sessions.SessionMiddleware, secret_key=session_crypto_key
        )

    @app.get("/")
    def root(request: fastapi.Request):
        """Redirects to the main gradio app if the user is authenticated, otherwise to the login gradio app."""
        username = get_username_if_authenticated(request)
        route = gradio_app_route if username else login_gradio_app_route
        redirect = starlette.responses.RedirectResponse(url=route)
        return redirect

    @app.route("/logout")
    async def logout(request: fastapi.Request):
        id_token = request.session.get("id_token")
        request.session.clear()
        if not end_session_endpoint or not id_token:
            url = "/"
        else:
            id_token = decompress(id_token)
            url = build_logout_redirect_url(
                end_session_endpoint=end_session_endpoint,
                post_logout_redirect_uri=request.url_for("root"),
                id_token=id_token,
            )

        redirect = starlette.responses.RedirectResponse(url=url)
        return redirect

    @app.route("/login")
    async def login(request: fastapi.Request):
        """Redirect to provider login page, which will redirect back to the redirect_url after authentication."""
        redirect_url = request.url_for("auth")
        redirect = await oauth_client.authorize_redirect(request, redirect_url)
        return redirect

    @app.route(auth_redirect_route)
    async def auth(request: fastapi.Request):
        """Try to fetch access token from provider. If successful, save userinfo in session to flag that the user is authenticated."""
        print("auth")
        try:
            access_token = await oauth_client.authorize_access_token(request)
        except authlib.integrations.starlette_client.OAuthError as e:
            url = build_url_with_parameters(
                login_gradio_app_route, error=e.error, description=e.description
            )
        else:
            access_token = dict(access_token)
            compressed_id_token = compress(access_token["id_token"])
            if len(compressed_id_token) <= max_id_token_size:
                request.session["id_token"] = compressed_id_token
            else:
                logging.warning("id_token is too large to be saved in session.")

            request.session["access_token_expires_at"] = access_token["expires_at"]
            request.session["user_info"] = filter_dict_by_keys(
                access_token["userinfo"], userinfo_fields
            )
            url = "/"

        redirect = starlette.responses.RedirectResponse(url)
        return redirect

    if not login_gradio_app:
        with gr.Blocks() as login_gradio_app:
            gr.Button("Login", link="/login")
            login_gradio_app.load(check_oauth_error_in_url_params)

    def auth_redirect_dependency(request: fastapi.Request) -> str | None:
        username = get_username_if_authenticated(request)
        if not username:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_307_TEMPORARY_REDIRECT,
                detail="Not authenticated",
                headers={"Location": str(request.url_for("root"))},
            )

        return username

    app = gr.mount_gradio_app(
        app,
        login_gradio_app,
        login_gradio_app_route,
        **(login_gradio_app_kwargs or {}),
    )
    app = gr.mount_gradio_app(
        app,
        gradio_app,
        gradio_app_route,
        auth_dependency=auth_redirect_dependency,
        **(gradio_app_kwargs or {}),
    )
    return app
