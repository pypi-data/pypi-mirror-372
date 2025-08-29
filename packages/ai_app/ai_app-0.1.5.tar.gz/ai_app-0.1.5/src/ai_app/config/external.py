from ai_app.external.gitlab import GitlabUrl
from ai_app.utils import PydanticForbidExtra


class JiraParameters(PydanticForbidExtra):
    url: str = "https://jira-support.kapitalbank.az"
    backoff_and_retry: bool = True
    retry_status_codes: list[int] = [400, 401, 413, 429, 503, 504]
    max_backoff_seconds: int = 10
    max_backoff_retries: int = 10


class ConfluenceParameters(PydanticForbidExtra):
    url: str = "https://confluence.kapitalbank.az"


class GitLabParameters(PydanticForbidExtra):
    url: GitlabUrl


class SonarQubeParameters(PydanticForbidExtra):
    url: str = "https://sonarqube.kapitalbank.az"
