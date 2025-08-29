from typing import override

import bir_mcp.config
import bir_mcp.sql
import langchain.tools

from ai_app.tools.base import BaseToolkit


class SqlToolkit(BaseToolkit):
    def __init__(
        self,
        sql_context: bir_mcp.config.SqlContext,
        max_tool_output_length: int | None = None,
    ):
        self.mcp = bir_mcp.sql.SQL(sql_context=sql_context)
        self.max_tool_output_length = max_tool_output_length

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = self.mcp.get_langchain_tools(
            max_output_length=self.max_tool_output_length,
            with_prefix=False,
        )
        return tools
