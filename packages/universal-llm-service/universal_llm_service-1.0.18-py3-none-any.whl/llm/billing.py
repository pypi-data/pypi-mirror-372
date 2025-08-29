import json
from typing import Any, AsyncGenerator, Awaitable, Callable, TypeVar

from langchain.schema import AIMessage, BaseMessage
from langchain_core.messages import BaseMessageChunk
from pydantic import BaseModel

from llm.counter import TokenCounter
from llm.pydantic_utils.checker import is_pydantic_instance

PydanticSchema = TypeVar('PydanticSchema', bound=BaseModel)


class BillingDecorator:
    """Декоратор для расчета токенов и расходов в USD при вызове LLM-функции."""

    def __init__(
        self,
        func: Callable[..., Awaitable[Any]],
        counter: TokenCounter,
    ) -> None:
        self.func = func
        self.counter = counter

    def __get__(self, instance, owner):
        return lambda *args, **kwargs: self(instance, *args, **kwargs)

    async def __call__(self, *args, **kwargs) -> BaseMessage:
        result: AIMessage | PydanticSchema = await self.func(*args, **kwargs)

        if isinstance(result, AIMessage):
            await self.counter.count_input_tokens(
                result.usage_metadata['input_tokens'],
            )
            await self.counter.count_output_tokens(
                result.usage_metadata['output_tokens'],
            )
        elif is_pydantic_instance(result):
            await self.counter.count_input_tokens_from_text(
                kwargs.get('input'),
            )

            result_dict = result.model_dump()
            output_text = json.dumps(result_dict, ensure_ascii=False)
            await self.counter.count_output_tokens_from_text(
                [AIMessage(content=output_text)],
            )

        return result


class StreamBillingDecorator:
    """Декоратор для расчета токенов и расходов в USD при стриминге LLM."""

    def __init__(
        self,
        func: Callable[..., AsyncGenerator[Any, None]],
        counter: TokenCounter,
    ) -> None:
        self.func = func
        self.counter = counter
        self.full_output_text = ''

    def __get__(self, instance, owner):
        return lambda *args, **kwargs: self(instance, *args, **kwargs)

    async def __call__(self, *args, **kwargs) -> AsyncGenerator[BaseMessageChunk, None]:
        self.full_output_text = ''

        stream = self.func(*args, **kwargs)
        async for chunk in stream:
            self.full_output_text += chunk.content
            yield chunk

        await self.counter.count_input_tokens_from_text(
            kwargs.get('input'),
        )
        await self.counter.count_output_tokens_from_text(
            [AIMessage(content=self.full_output_text)],
        )
