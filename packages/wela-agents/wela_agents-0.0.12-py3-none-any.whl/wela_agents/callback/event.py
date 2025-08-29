
from abc import ABC
from typing import Any
from typing import Dict

from wela_agents.toolkit.tool_result import ToolResult

class Event(ABC):
    pass

class ToolEvent(Event):

    def __init__(self, tool_name: str, arguments: Dict[str, Any], result: ToolResult = None) -> None:
        super().__init__()
        self.__tool_name = tool_name
        self.__arguments = arguments
        self.__result = result

    @property
    def tool_name(self) -> str:
        return self.__tool_name

    @property
    def arguments(self) -> Dict[str, Any]:
        return self.__arguments

    @property
    def result(self) -> ToolResult:
        return self.__result

__all__ = [
    "Event",
    "ToolEvent"
]
