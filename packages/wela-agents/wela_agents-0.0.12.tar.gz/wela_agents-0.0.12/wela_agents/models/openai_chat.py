
import httpx

from typing import Dict
from typing import List
from typing import Union
from typing import Optional
from typing import Generator
from typing_extensions import Literal
from openai import OpenAI
from openai import Stream
from openai.types.chat import ChatCompletion
from openai.types.chat import ChatCompletionChunk
from openai.types.chat import ChatCompletionToolParam
from openai.types.chat.completion_create_params import ResponseFormat
from wela_agents.models.model import Model
from wela_agents.schema.prompt.openai_chat import Message
from wela_agents.schema.prompt.openai_chat import AIMessage

class OpenAIChat(Model[Message]):
    def __init__(
        self,
        *,
        model_name: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: Optional[Literal[False]] | Literal[True] = None
    ) -> None:
        super().__init__()
        self.__model_name: str = model_name
        self.__client: OpenAI = OpenAI(api_key=api_key, base_url=base_url)
        self.__temperature: Optional[float] = temperature
        self.__top_p: Optional[float] = top_p
        self.__frequency_penalty: Optional[float] = frequency_penalty
        self.__presence_penalty: Optional[float] = presence_penalty
        self.__stream: Optional[Literal[False]] | Literal[True] = stream

    @property
    def model_name(self) -> str:
        return self.__model_name

    @property
    def streaming(self) -> bool:
        return self.__stream is True

    def __create(
        self,
        *,
        messages: List[Message],
        reasoning_effort: Optional[Literal["minimal", "low", "medium", "high"]] = None,
        verbosity: Optional[Literal['low', 'medium', 'high']]= None,
        n: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        stop: Union[Optional[str], List[str], None] = None,
        response_format : ResponseFormat = None,
        tools: List[ChatCompletionToolParam] = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
        params: Dict = {
            "model": self.__model_name,
            "stream": self.__stream,
            "messages": messages,
            "n": n,
            "stop": stop,
            "temperature": self.__temperature,
            "top_p": self.__top_p,
            "frequency_penalty": self.__frequency_penalty,
            "presence_penalty": self.__presence_penalty,
            "tools": tools,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs
        }
        if self.__model_name in [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-5-2025-08-07",
            "gpt-5-mini-2025-08-07",
            "gpt-5-nano-2025-08-07",
            "gpt-5-chat-latest",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-mini-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "o4-mini",
            "o4-mini-2025-04-16",
            "o3",
            "o3-2025-04-16",
            "o3-mini",
            "o3-mini-2025-01-31",
            "o1",
            "o1-2024-12-17",
            "o1-preview",
            "o1-preview-2024-09-12",
            "o1-mini",
            "o1-mini-2024-09-12",
            "gpt-4o",
            "gpt-4o-2024-11-20",
            "gpt-4o-2024-08-06",
            "gpt-4o-2024-05-13",
            "gpt-4o-audio-preview",
            "gpt-4o-audio-preview-2024-10-01",
            "gpt-4o-audio-preview-2024-12-17",
            "gpt-4o-audio-preview-2025-06-03",
            "gpt-4o-mini-audio-preview",
            "gpt-4o-mini-audio-preview-2024-12-17",
            "gpt-4o-search-preview",
            "gpt-4o-mini-search-preview",
            "gpt-4o-search-preview-2025-03-11",
            "gpt-4o-mini-search-preview-2025-03-11",
            "chatgpt-4o-latest",
            "codex-mini-latest",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09",
            "gpt-4-0125-preview",
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-16k-0613",
        ]:
            params.update({
                "max_completion_tokens": max_completion_tokens
            })
        else:
            params.update({
                "max_tokens": max_completion_tokens
            })
        if tools != None:
            params.update({
                "parallel_tool_calls": False
            })
        if response_format != None:
            params.update({
                "response_format": response_format
            })
        if self.__model_name in [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-5-2025-08-07",
            "gpt-5-mini-2025-08-07",
            "gpt-5-nano-2025-08-07",
            "gpt-5-chat-latest"
        ]:
            params.update({
                "reasoning_effort": reasoning_effort,
                "verbosity": verbosity
            })
        return self.__client.chat.completions.create(**{k: v for k, v in params.items() if v != None})

    def predict(self, **kwargs) -> Union[List[Message], Generator[List[Message], None, None]]:

        assert "messages" in kwargs, "messages is required"

        messages: List[Message] = kwargs["messages"]
        reasoning_effort: Optional[Literal["minimal", "low", "medium", "high"]] = kwargs.get("reasoning_effort", None)
        verbosity: Optional[Literal['low', 'medium', 'high']] = kwargs.get("verbosity", None)
        n: Optional[int] = kwargs.get("n", None)
        max_completion_tokens: Optional[int] = kwargs.get("max_completion_tokens", None)
        
        stop: Union[Optional[str], List[str], None] = kwargs.get("stop", None)
        response_format : ResponseFormat = kwargs.get("response_format", None)
        tools: List[ChatCompletionToolParam] = kwargs.get("tools", None)

        logprobs: bool | None = kwargs.get("logprobs", None)
        top_logprobs: int | None = kwargs.get("top_logprobs", None)

        try:
            completions = self.__create(
                messages=messages,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
                n=n,
                max_completion_tokens=max_completion_tokens,
                stop=stop,
                response_format=response_format,
                tools=tools,
                logprobs=logprobs,
                top_logprobs=top_logprobs
            )
            if not self.__stream:
                return [choice.message.to_dict() for choice in completions.choices]
            def stream():
                for chunk in completions:
                    messages = [None for _ in range(1 if n == None else n)]
                    for choice in chunk.choices:
                        index = choice.index
                        messages[index] = choice.delta.to_dict()
                        if not choice.finish_reason:
                            yield messages
            return stream()
        except Exception as e:
            if not self.__stream:
                return [AIMessage(role="assistant", content=f"{e}")]
            else:
                def stream(e: Exception):
                    yield [AIMessage(role="assistant", content=f"{e}") for _ in range(1 if n == None else n)]
            return stream(e)

__all__ = [
    "OpenAIChat"
]
