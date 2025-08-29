from abc import ABC, abstractmethod

import langchain.tools


class BaseToolkit(ABC):
    @abstractmethod
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        """For compatibility with langchain_core.tools.BaseToolkit."""

    def get_named_tools(self) -> dict[str, langchain.tools.BaseTool]:
        tools = self.get_tools()
        tools = {tool.name: tool for tool in tools}
        return tools
