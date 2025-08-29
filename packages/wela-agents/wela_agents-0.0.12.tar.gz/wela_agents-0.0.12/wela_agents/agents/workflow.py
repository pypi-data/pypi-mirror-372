
from typing import Any
from typing import Dict
from typing import Union
from typing import Callable
from typing import Generator

from wela_agents.agents.agent import Agent

START = "__WORKFLOW_START_POINT__"
END = "__WORKFLOW_END_POINT__"

class StatefulAgent(Agent):
    """
    An agent that maintains state across calls.
    """

    @property
    def state(self) -> str:
        return self.__state

    def __init__(self, *, state: Dict[Any, Any], input_key: str, output_key: str) -> None:
        super().__init__(input_key=input_key, output_key=output_key)
        self.__state: Dict[Any, Any] = state

class Workflow(StatefulAgent):
    """
    A workflow agent that manages a sequence of agents with state and conditions.
    It allows for dynamic routing based on conditions and maintains state across agent calls.
    This agent can be used to create complex workflows where the next agent to call
    can depend on the current state or the output of previous agents.
    """

    def __init__(self, *, state: Dict[Any, Any], input_key: str, output_key: str) -> None:
        super().__init__(state=state, input_key=input_key, output_key=output_key)
        self.__agent_mapping: Dict[StatefulAgent, Dict[Any, StatefulAgent]] = {}

    def add_mapping(self, from_agent: StatefulAgent, to_agent: StatefulAgent) -> None:
        self.add_conditional_mapping(from_agent, None, to_agent)

    def add_conditional_mapping(self, agent: StatefulAgent, condition: Callable, choice: Union[Dict[Any, StatefulAgent], StatefulAgent] = None) -> None:
        self.__agent_mapping[agent] = {
            "condition": condition,
            "choice": choice if choice is not None else {}
        }

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        current_agent = START
        while True:
            next = self.__agent_mapping[current_agent]
            if next["condition"]:
                condition = next["condition"](self.state)
                current_agent = next["choice"].get(condition, None)
            else:
                current_agent = next["choice"]
            if current_agent == END:
                break
            prediction = current_agent.predict(**kwargs)
            kwargs[current_agent.output_key] = prediction
        return prediction

__all__ = [
    "StatefulAgent",
    "Workflow"
]
