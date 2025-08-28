from typing import override

import bir_mcp
import langchain.tools

from ai_app.tools.base import BaseToolkit


class GitLabToolkit(BaseToolkit):
    def __init__(
        self,
        url: str,
        private_token: str,
        timezone: str = "UTC",
        max_tool_output_length: int | None = None,
    ):
        super().__init__()
        self.mcp = bir_mcp.git_lab.GitLab(url=url, private_token=private_token, timezone=timezone)
        self.max_tool_output_length = max_tool_output_length

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            self.mcp.get_merge_request_overview_from_url,
            self.mcp.get_file_content,
            self.mcp.get_merge_request_file_diffs,
            self.mcp.comment_on_merge_request,
        ]
        tools = [
            bir_mcp.utils.to_langchain_tool(
                tool, prefix=self.mcp.get_tag(), max_output_length=self.max_tool_output_length
            )
            for tool in tools
        ]
        return tools
