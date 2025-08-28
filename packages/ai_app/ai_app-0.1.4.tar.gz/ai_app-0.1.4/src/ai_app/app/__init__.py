import fastapi.middleware.cors
import fastapi.responses
import gradio as gr
import logfire

from ai_app.auth import mount_auth_for_gradio_app
from ai_app.config import get_config, get_favicon_path

from .gradio import build_page
from .middleware import add_middleware


def build_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    config = get_config()
    config.setup_logging()
    oauth = config.build_oauth()
    no_auth_params = config.get_gradio_app_kwargs(auth=False)
    if not oauth:
        gradio_app = build_page()
        app = gr.mount_gradio_app(app, gradio_app, config.gradio_app_route, **no_auth_params)

        @app.get("/")
        def root():
            return fastapi.responses.RedirectResponse(url=config.gradio_app_route)

    else:
        gradio_app = build_page(assume_auth=False)
        gradio_app_auth = build_page(assume_auth=True)
        auth_params = config.get_gradio_app_kwargs(auth=True)
        app = mount_auth_for_gradio_app(
            app=app,
            oauth_client=oauth.starlette_client,
            gradio_app=gradio_app_auth,
            login_gradio_app=gradio_app,
            login_gradio_app_route=config.gradio_login_app_route,
            gradio_app_route=config.gradio_app_route,
            auth_redirect_route=config.auth_route,
            end_session_endpoint=oauth.openid_metadata["end_session_endpoint"],
            max_id_token_size=config.max_id_token_size,
            login_gradio_app_kwargs=no_auth_params,
            gradio_app_kwargs=auth_params,
            userinfo_fields=config.user_info_fields,
        )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return fastapi.responses.FileResponse(get_favicon_path())

    add_middleware(app)
    logfire.instrument_fastapi(app, excluded_urls=[".*/gradio_api/heartbeat.*"])
    return app
