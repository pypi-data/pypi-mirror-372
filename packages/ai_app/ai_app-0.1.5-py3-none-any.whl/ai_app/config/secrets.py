import pydantic

from ai_app.external.providers import ModelProvider
from ai_app.utils import PydanticForbidExtra


class Secrets(PydanticForbidExtra):
    openai_api_key: pydantic.SecretStr
    google_api_key: pydantic.SecretStr
    azure_openai_api_key: pydantic.SecretStr | None = None
    langsmith_api_key: pydantic.SecretStr | None = None
    jira_api_token: pydantic.SecretStr | None = None
    confluence_api_token: pydantic.SecretStr | None = None
    gitlab_api_key: pydantic.SecretStr | None = None
    sonarqube_api_key: pydantic.SecretStr | None = None
    session_crypto_key: pydantic.SecretStr | None = None
    oauth_client_id: pydantic.SecretStr | None = None
    oauth_client_secret: pydantic.SecretStr | None = None
    logfire_api_token: pydantic.SecretStr | None = None
    google_service_account_info: pydantic.SecretStr | None = None
    google_authorized_user_info: pydantic.SecretStr | None = None

    @property
    def provider_api_keys(self) -> dict[ModelProvider, pydantic.SecretStr]:
        return {
            ModelProvider.openai: self.openai_api_key.get_secret_value(),
            ModelProvider.google_genai: self.google_api_key.get_secret_value(),
            ModelProvider.azure_openai: self.azure_openai_api_key.get_secret_value()
            if self.azure_openai_api_key
            else None,
        }
