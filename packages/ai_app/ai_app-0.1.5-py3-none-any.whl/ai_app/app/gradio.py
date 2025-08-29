import datetime
import functools
import importlib
import logging

import gradio as gr

from ai_app.auth import check_oauth_error_in_url_params
from ai_app.config import get_config
from ai_app.core import BaseApp, State
from ai_app.frontend import build_model_choice_dropdown, get_generating_text_javascript
from ai_app.utils import Timer, get_pydantic_model_fields


@functools.cache
def try_build_module_app(module_name: str) -> BaseApp | None:
    try:
        app_module = importlib.import_module(f"ai_app.apps.{module_name}")
    except ImportError:
        logging.error(
            f"Failed to import {module_name} module, probably because of missing optional packages",
            exc_info=True,
        )
        return

    with Timer(f"Initializing app '{app_module.App.name}'"):
        app = app_module.App()

    return app


def build_tab_app(module_name: str, assume_auth: bool, model_choice: gr.Dropdown):
    app = try_build_module_app(module_name)
    if not app or app.requires_auth and not assume_auth:
        return

    # For some reason, the scale argument needs to be passed to make tab fill height.
    with gr.Tab(app.name, scale=1):
        with Timer(f"Building app '{app.name}'"):
            app.build_gradio_blocks(model_choice=model_choice)


def build_tabs(assume_auth: bool, model_choice: gr.Dropdown):
    # Todo: maybe make dynamic at runtime based on "show" values in config.
    for module_name, app_config in get_pydantic_model_fields(get_config().apps).items():
        if app_config.show:
            build_tab_app(
                module_name=module_name,
                assume_auth=assume_auth,
                model_choice=model_choice,
            )


def display_username(request: gr.Request) -> str | None:
    try:
        user_info = State.from_request(request)
    except AssertionError:
        # Catch AssertionError: SessionMiddleware must be installed to access request.session
        return

    if not user_info.name:
        return

    return f"Welcome, {user_info.name}"


def build_page(
    assume_auth: bool | None = None,
    analytics_enabled: bool = False,
    delete_cache_frequency: datetime.timedelta = datetime.timedelta(hours=1),
    delete_cache_age: datetime.timedelta = datetime.timedelta(days=1),
    fill_height: bool = True,
) -> gr.Blocks:
    with gr.Blocks(
        analytics_enabled=analytics_enabled,
        delete_cache=(
            int(delete_cache_frequency.total_seconds()),
            int(delete_cache_age.total_seconds()),
        ),
        fill_height=fill_height,
        js=get_generating_text_javascript(),
    ) as gradio_app:
        with gr.Row():
            model_choice = build_model_choice_dropdown(models=get_config().model_choices)
            if assume_auth is not None:
                markdown = gr.Markdown(rtl=True)
                if assume_auth:
                    gr.Button("Logout", link="/logout")
                    gradio_app.load(display_username, outputs=markdown)
                else:
                    gr.Button("Login", link="/login")
                    gradio_app.load(check_oauth_error_in_url_params)

        build_tabs(assume_auth=bool(assume_auth), model_choice=model_choice)

    return gradio_app


gr.Tab
