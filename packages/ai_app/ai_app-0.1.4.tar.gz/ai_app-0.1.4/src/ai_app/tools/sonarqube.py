from typing import override

import bir_mcp
import langchain.tools

from ai_app.tools.base import BaseToolkit


class SonarQubeToolkit(BaseToolkit):
    def __init__(
        self,
        url: str,
        token: str,
        gitlab_url: str,
        timezone: str = "UTC",
        max_tool_output_length: int | None = None,
    ):
        super().__init__()
        self.mcp = bir_mcp.git_lab.SonarQube(
            url=url, gitlab_url=gitlab_url, token=token, timezone=timezone
        )
        self.max_tool_output_length = max_tool_output_length

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            self.mcp.get_project_quality_gates_status,
            self.mcp.get_main_project_metrics,
        ]
        tools = [
            bir_mcp.utils.to_langchain_tool(
                tool, prefix=self.mcp.get_tag(), max_output_length=self.max_tool_output_length
            )
            for tool in tools
        ]
        return tools
