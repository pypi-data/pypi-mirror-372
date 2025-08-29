
from typing import Any
from typing import List
from typing import Union
from typing import Callable
from typing import Generator

from wela_agents.agents.agent import Agent

class SimpleSequentialAgent(Agent):

    def __init__(self, *, agents: List[Agent], input_key: str = "__input__", output_key: str = "__output__") -> None:
        self.__agents: List[Agent] = agents
        super().__init__(input_key=input_key, output_key=output_key)

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        prediction = None
        for agent in self.__agents:
            prediction = agent.predict(**kwargs)
            kwargs[agent.output_key] = prediction
        return prediction

class CycleSequentialAgent(Agent):

    def __init__(self, *, agents: List[Agent], condition: Callable = None, input_key: str = "__input__", output_key: str = "__output__") -> None:
        self.__agents: List[Agent] = agents
        self.__condition: Callable = condition
        super().__init__(input_key=input_key, output_key=output_key)

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        prediction = None
        while True:
            for agent in self.__agents:
                prediction = agent.predict(**kwargs)
                kwargs[agent.output_key] = prediction
            if self.__condition is None or not self.__condition(**kwargs):
                break
        return prediction

__all__ = [
    "CycleSequentialAgent",
    "SimpleSequentialAgent"
]
