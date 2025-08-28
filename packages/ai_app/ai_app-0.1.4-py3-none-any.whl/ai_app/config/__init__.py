import enum
import functools
import os
import pathlib

import alembic.config
import atlassian
import bir_mcp.config
import httpx
import langchain.chat_models
import logfire
import pydantic
import sqlalchemy as sa
import yaml

import ai_app
from ai_app.ai_utils import set_langsmith_environment_variables
from ai_app.auth import OAuth
from ai_app.config.ai import ChatModelParameters
from ai_app.config.apps import Apps
from ai_app.config.external import (
    ConfluenceParameters,
    GitLabParameters,
    JiraParameters,
    SonarQubeParameters,
)
from ai_app.config.middleware import CorsConfig, EndpointRateLimitConfig, RateLimitConfig
from ai_app.config.secrets import Secrets
from ai_app.config.sql import Connection, ConnectionContext
from ai_app.external.consul import ConsulKeyValue
from ai_app.external.google import Spreadsheets, build_spreadsheets
from ai_app.external.providers import ModelProvider
from ai_app.frontend import filter_common_model_names
from ai_app.pii import AnonCodec, EntityTypeCodec
from ai_app.tools import ConfluenceToolkit, GitLabToolkit, JiraToolkit, SonarQubeToolkit, SqlToolkit
from ai_app.utils import (
    PydanticForbidExtra,
    get_module_path,
    join_url,
    refreshing_cache,
    setup_logging,
)


def get_project_src_path() -> pathlib.Path:
    return get_module_path(ai_app).parent


def to_absolute_path(path: pathlib.Path | str) -> pathlib.Path:
    path = pathlib.Path(path)
    if not path.is_absolute():
        path = get_project_src_path() / path

    path = path.resolve()
    return path


class Stage(enum.StrEnum):
    local = enum.auto()
    dev = enum.auto()
    preprod = enum.auto()
    prod = enum.auto()


class ObservabilityPlatform(enum.StrEnum):
    langsmith = enum.auto()
    langfuse = enum.auto()
    opik = enum.auto()


def get_favicon_path():
    return to_absolute_path("static/favicon_1.png")


class Config(PydanticForbidExtra):
    stage: Stage
    secrets: Secrets
    jira_parameters: JiraParameters
    confluence_parameters: ConfluenceParameters
    gitlab_parameters: GitLabParameters
    sonarqube_parameters: SonarQubeParameters
    observability_platform: ObservabilityPlatform | None = None
    enable_logfire: bool = True
    instrument_sqlalchemy: bool = False
    project: str = "ai_app"
    model_choices: list[str] = filter_common_model_names(
        max_cost=5, supports_system_messages=True, providers=[ModelProvider.openai]
    )
    azure_endpoint: str = "https://itopsai.openai.azure.com/"
    azure_api_version: str = "2024-12-01-preview"
    sanitation_deny_list: list[str] = []
    sanitation_replacing_format: str = "{{{entity_type}_{index}}}"  # Angular brackets get mixed up with HTML tags in Gradio messages.
    apps: Apps
    port: int = 7860
    gradio_login_app_route: str = "/gradio-login"
    gradio_app_route: str = "/gradio"
    auth_route: str = "/auth"
    public_url: str | None = None
    oauth_provider_url: str | None = None
    max_id_token_size: int = 0
    cors_config: CorsConfig = CorsConfig()
    file_size_mb_limit_no_auth: int = 5
    file_size_mb_limit_auth: int = 50
    security_headers: dict[str, str] = {
        "X-Frame-Options": "SAMEORIGIN",
        "Content-Security-Policy": "frame-ancestors 'self';",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    user_info_fields: list[str] = ["employeeID", "preferred_username", "name", "email"]
    sql_connections: dict[str, Connection] = {}
    sql_connection_contexts: dict[str, ConnectionContext] = {}
    # When switching between chats, the gr.State gets shared between them, which may lead to context
    # leaking. To fix it, need to store a state for each thread_id.
    common_chat_interface_parameters: dict = dict(save_history=False)
    rate_limit_config: RateLimitConfig = RateLimitConfig()
    timezone: str = "Asia/Baku"
    max_tool_output_length: int | None = None
    ca_file: str | None = None

    @property
    def project_with_stage(self) -> str:
        return f"{self.project}_{self.stage}"

    @property
    def is_prod(self) -> bool:
        return self.stage == Stage.prod

    @property
    def is_local(self) -> bool:
        return self.stage == Stage.local

    @property
    def redirect_uri(self) -> str:
        url = self.public_url if self.is_prod else "http://localhost"
        url = join_url(url, self.auth_route)
        return url

    @pydantic.model_validator(mode="after")
    def _validate(cls, self):
        for connection_context in self.sql_connection_contexts.values():
            if connection_context.connection_name not in self.sql_connections:
                raise ValueError(
                    f"Connection '{connection_context.connection_name}' not found in 'sql_connections'"
                )

        return self

    def model_post_init(self, _context):
        if self.is_local:
            self.cors_config.allow_origin_regex = "http://localhost:.*"
            self.cors_config.allow_credentials = True

        if self.public_url:
            self.cors_config.allow_origins.append(self.public_url)

        if self.ca_file:
            bir_mcp.utils.set_ssl_cert_file_from_cadata(self.ca_file)

    def setup_logging(self):
        """
        Calling this function twice may lead to an error.
        Httpx and fastapi packages need to be instrumented per client and app respectively:
            logfire.instrument_fastapi(app)
        """
        match self.observability_platform:
            case ObservabilityPlatform.langsmith:
                set_langsmith_environment_variables(
                    langsmith_api_key=self.secrets.langsmith_api_key.get_secret_value(),
                    langsmith_project=self.project_with_stage,
                )

        if self.enable_logfire:
            logfire.configure(
                environment=str(self.stage),
                token=self.secrets.logfire_api_token.get_secret_value(),
                scrubbing=False if self.is_local else None,
                send_to_logfire=True,
            )
            logfire.instrument_system_metrics()
            logfire.instrument_pydantic(record="failure")
            logfire.instrument_httpx(
                capture_request_body=self.is_local,
                capture_response_body=self.is_local,
            )
            if self.instrument_sqlalchemy:  # if self.is_local:
                # Logs every SQL query, which is overkill for most cases.
                logfire.instrument_sqlalchemy()

        setup_logging(handlers=[logfire.LogfireLoggingHandler()])

    @staticmethod
    def from_consul():
        consul_key_value = ConsulKeyValue.from_env_variables()
        value = consul_key_value.load()
        config = yaml.safe_load(value)
        config = Config(**config)
        return config

    def get_jira_kwargs(self) -> dict:
        kwargs = self.jira_parameters.model_dump()
        if self.secrets.jira_api_token:
            kwargs["token"] = self.secrets.jira_api_token.get_secret_value()

        return kwargs

    def get_jira_toolkit_kwargs(self) -> dict:
        kwargs = self.get_jira_kwargs()
        kwargs |= self.model_dump(include={"max_tool_output_length"})
        return kwargs

    def get_confluence_toolkit_kwargs(self) -> dict:
        kwargs = self.confluence_parameters.model_dump()
        kwargs |= self.model_dump(include={"max_tool_output_length"})
        if self.secrets.confluence_api_token:
            kwargs["token"] = self.secrets.confluence_api_token.get_secret_value()

        return kwargs

    def get_gitlab_kwargs(self) -> dict:
        kwargs = self.gitlab_parameters.model_dump()
        kwargs |= self.model_dump(include={"timezone", "max_tool_output_length"})
        if self.secrets.gitlab_api_key:
            kwargs["private_token"] = self.secrets.gitlab_api_key.get_secret_value()

        return kwargs

    def get_sonarqube_kwargs(self) -> dict:
        kwargs = self.sonarqube_parameters.model_dump()
        kwargs |= self.model_dump(include=["timezone", "max_tool_output_length"])
        kwargs["gitlab_url"] = self.gitlab_parameters.url
        if self.secrets.sonarqube_api_key:
            kwargs["token"] = self.secrets.sonarqube_api_key.get_secret_value()

        return kwargs

    def build_oauth(self) -> OAuth | None:
        if not self.oauth_provider_url:
            return

        # Verify provider reachability (timeout/error -> skip OAuth setup).
        try:
            response = httpx.get(self.oauth_provider_url, timeout=5.0)
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError):
            return

        oauth = OAuth(
            provider_base_url=self.oauth_provider_url,
            client_id=self.secrets.oauth_client_id.get_secret_value(),
            client_secret=self.secrets.oauth_client_secret.get_secret_value(),
            redirect_uri=self.redirect_uri,
        )
        return oauth

    def get_gradio_app_kwargs(self, auth: bool = False) -> dict:
        max_file_size_mb = self.file_size_mb_limit_auth if auth else self.file_size_mb_limit_no_auth
        kwargs = dict(
            max_file_size=f"{max_file_size_mb}mb",
            show_error=not self.is_prod,
            enable_monitoring=not self.is_prod,
            allowed_paths=[get_favicon_path()],
        )
        return kwargs

    def build_entity_codec(self) -> EntityTypeCodec:
        codec = EntityTypeCodec(replacing_format=self.sanitation_replacing_format)
        return codec

    def get_provider_api_key(self, provider: ModelProvider) -> pydantic.SecretStr | None:
        provider_api_keys = self.secrets.provider_api_keys
        api_key = provider_api_keys.get(provider)
        return api_key

    def build_chat_model_parameters(self, model: str):
        parameters = ChatModelParameters.from_model_name(model)
        parameters.api_key = self.get_provider_api_key(parameters.model_provider)
        return parameters


@refreshing_cache()
def get_config() -> Config:
    try:
        config = Config.from_consul()
    except KeyError:
        config_path = os.getenv("CONFIG_PATH")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        config = Config(**config)

    return config


def get_jira_kwargs() -> dict:
    return get_config().get_jira_kwargs()


def get_gitlab_kwargs() -> dict:
    return get_config().get_gitlab_kwargs()


@functools.cache
def get_chat_model(model_name: str):
    config = get_config()
    if model_name.startswith("azure"):
        model_name = model_name.removeprefix("azure-")
        provider = ModelProvider.azure_openai
        model = langchain.chat_models.init_chat_model(
            model_name,
            model_provider=provider,
            azure_endpoint=config.azure_endpoint,
            api_version=config.azure_api_version,
            azure_deployment=model_name,
            api_key=config.get_provider_api_key(provider),
        )
        return model

    return config.build_chat_model_parameters(model_name).build_model()


@functools.cache
def get_engine(connection_name: str) -> sa.Engine:
    return get_config().sql_connections[connection_name].build_engine()


@functools.cache
def get_ai_postgres_engine() -> sa.Engine:
    return get_engine("postgres_ai")


@functools.cache
def get_ai_postgres_rag_engine() -> sa.Engine:
    return get_engine("postgres_ai_rag")


@functools.cache
def get_jira():
    return atlassian.Jira(**get_jira_kwargs())


@functools.cache
def get_service_desk():
    return atlassian.ServiceDesk(**get_jira_kwargs())


@functools.cache
def get_jira_toolkit():
    return JiraToolkit(**get_config().get_jira_toolkit_kwargs())


@functools.cache
def get_confluence_toolkit():
    return ConfluenceToolkit(**get_config().get_confluence_toolkit_kwargs())


@functools.cache
def get_gitlab_toolkit():
    return GitLabToolkit(**get_gitlab_kwargs())


@functools.cache
def get_sonarqube_toolkit():
    return SonarQubeToolkit(**get_config().get_sonarqube_kwargs())


@functools.cache
def get_anon_codec():
    return AnonCodec(deny_list=get_config().sanitation_deny_list)


@functools.cache
def get_sql_toolkit(connection_context_name: str) -> SqlToolkit:
    connection_context = get_config().sql_connection_contexts[connection_context_name]
    connection = get_config().sql_connections[connection_context.connection_name]
    sql_context = bir_mcp.config.SqlContext(
        connection=connection.model_dump(),
        schema_tables=connection_context.schema_tables,
    )
    toolkit = SqlToolkit(
        sql_context=sql_context,
        max_tool_output_length=get_config().max_tool_output_length,
    )
    return toolkit


def get_alembic_config(
    alembic_ini: str = "alembic.ini", alembic_directory: str = "alembic"
) -> alembic.config.Config:
    project_root_path = get_project_src_path().parent
    config = alembic.config.Config(project_root_path / alembic_ini)
    config.set_main_option("script_location", str(project_root_path / alembic_directory))
    return config


@functools.cache
def get_jira_service_desk_spreadsheets() -> Spreadsheets:
    spreadsheets = build_spreadsheets(
        spreadsheet_id=get_config().apps.jira_service_desk.jira_requests_spreadsheet_id,
        service_account_info=get_config().secrets.google_service_account_info.get_secret_value(),
    )
    return spreadsheets


def get_judge_model_names() -> list[str]:
    models = [
        "gpt-4.1",
        "gpt-5",
        # "gemini-2.5-pro",
        # "anthropic/claude-4-sonnet",
    ]
    return models
