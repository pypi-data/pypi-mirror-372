
import json

from typing import Any
from typing import Dict
from typing import List

from wela_agents.toolkit.tool import Tool
from wela_agents.toolkit.tool_result import ToolResult
from wela_agents.callback.event import ToolEvent
from wela_agents.callback.callback import ToolCallback
from wela_agents.schema.prompt.openai_chat import Function

class Toolkit(Dict[str, Tool]):

    def __init__(self, tools: List[Tool], callback: ToolCallback = None) -> None:
        for tool in tools:
            self[tool.name] = tool
        self.__callback = callback

    def add_tool(self, tool: Tool) -> None:
        self[tool.name] = tool

    def set_callback(self, callback: ToolCallback) -> None:
        self.__callback = callback

    def run(self, function: Function) -> ToolResult:
        tool_name = function.get("name")
        arguments_str = function.get("arguments")

        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            return ToolResult(result="Error: Invalid JSON format for arguments.")

        if tool_name not in self:
            return ToolResult(result=f"Error: Tool '{tool_name}' not found.")

        tool = self[tool_name]

        if self.__callback:
            event = ToolEvent(tool_name, arguments)
            self.__callback.before_tool_call(event)

        try:
            if self.__callback:
                result = tool.run(self.__callback.update_progress, **arguments)
            else:
                result = tool.run(None, **arguments)
        except Exception as e:
            return ToolResult(result=f"Error: An error occurred while running the tool - {str(e)}")

        if self.__callback:
            event = ToolEvent(tool_name, arguments, result)
            self.__callback.after_tool_call(event)

        return result

    def to_tools_param(self) -> List[Dict[str, Any]]:
        return [tool.to_tool_param() for tool in self.values()]

__all__ = [
    "Toolkit"
]
