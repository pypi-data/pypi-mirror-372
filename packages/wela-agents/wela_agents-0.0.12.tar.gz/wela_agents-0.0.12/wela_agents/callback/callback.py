
from wela_agents.callback.event import ToolEvent

class Callback():
    pass

class ToolCallback(Callback):

    def before_tool_call(self, _: ToolEvent) -> None:
        pass

    def update_progress(self, _: ToolEvent) -> None:
        pass

    def after_tool_call(self, _: ToolEvent) -> None:
        pass

__all__ = [
    "Callback",
    "ToolCallback"
]
