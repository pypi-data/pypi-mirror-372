
import time

from typing import Any
from typing import List
from typing import Union
from typing import Optional
from typing import Generator
from typing_extensions import Literal

from wela_agents.memory.memory import Memory
from wela_agents.toolkit.toolkit import Toolkit
from wela_agents.models.model import Model
from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.agents.conversation import ConversationAgent
from wela_agents.retriever.retriever import Retriever
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import MessageTemplate
from wela_agents.schema.template.openai_chat import MessagePlaceholder
from wela_agents.schema.template.openai_chat import SystemMessageTemplate
from wela_agents.schema.template.prompt_template import PromptTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

default_prompt = '''You are ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture.'''

class Meta(ConversationAgent):
    def __init__(
        self,
        *,
        model: Model,
        prompt: str = default_prompt,
        reasoning_effort: Optional[Literal["minimal", "low", "medium", "high"]] = None,
        verbosity: Literal['low', 'medium', 'high'] | None = None,
        max_completion_tokens: Optional[int] = None,
        memory: Memory = None,
        toolkit: Toolkit = None,
        retriever: Retriever = None,
        input_key: str = "__input__",
        output_key: str = "__output__"
    ) -> None:
        assert isinstance(model, OpenAIChat), "Unsupported model type"

        if isinstance(model, OpenAIChat):
            message_template_list: List[MessageTemplate] = []
            message_template_list.append(SystemMessageTemplate(StringPromptTemplate(prompt)))
            if memory:
                message_template_list.append(MessagePlaceholder(placeholder_key = memory.memory_key))
            if retriever:
                message_template_list.append(MessagePlaceholder(placeholder_key = retriever.retriever_key))
            message_template_list.append(SystemMessageTemplate(StringPromptTemplate("{__system_hint__}")))
            message_template_list.append(MessagePlaceholder(placeholder_key = input_key))
            prompt_template: PromptTemplate = ChatTemplate(message_template_list)

        super().__init__(
            model = model,
            prompt_template = prompt_template,
            reasoning_effort = reasoning_effort,
            verbosity = verbosity,
            max_completion_tokens = max_completion_tokens,
            toolkit = toolkit,
            memory = memory,
            retriever = retriever,
            input_key = input_key,
            output_key = output_key
        )

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        kwargs["__system_hint__"] = "Current time is: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        return super().predict(**kwargs)

__all__ = [
    "Meta"
]
