from typing import override

import atlassian
import bir_mcp
import langchain.tools

from ai_app.external.atlassian import get_project_overview
from ai_app.tools.base import BaseToolkit


class JiraToolkit(BaseToolkit):
    def __init__(
        self,
        token: str,
        url: str,
        api_version: int = 2,
        max_tool_output_length: int | None = None,
        **kwargs,  # The kwargs from JiraParameters, need to use them for tenacity manually instead of passing to atlassian.Jira.
    ):
        super().__init__()
        self.mcp = bir_mcp.atlassian.Jira(token=token, url=url, api_version=api_version, **kwargs)
        self.max_tool_output_length = max_tool_output_length
        self.jira = atlassian.Jira(token=token, url=url, api_version=api_version, **kwargs)

    def get_jira_project_overview(self, project_key: str) -> dict:
        """Fetches the overview of a Jira project."""
        overview = get_project_overview(self.jira, project_key)
        return overview

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            self.mcp.get_issue_overview,
            self.get_jira_project_overview,
        ]
        tools = [
            bir_mcp.utils.to_langchain_tool(tool, max_output_length=self.max_tool_output_length)
            for tool in tools
        ]
        return tools


class ConfluenceToolkit(BaseToolkit):
    def __init__(self, token: str, url: str, max_tool_output_length: int | None = None):
        super().__init__()
        self.mcp = bir_mcp.atlassian.Confluence(token=token, url=url)
        self.max_tool_output_length = max_tool_output_length

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = self.mcp.get_langchain_tools(max_output_length=self.max_tool_output_length)
        return tools
