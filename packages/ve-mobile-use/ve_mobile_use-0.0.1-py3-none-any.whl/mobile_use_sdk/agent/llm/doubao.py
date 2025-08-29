# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging

from langchain_core.messages import BaseMessage
from langchain_deepseek import ChatDeepSeek
from openai import OpenAI

from mobile_use_sdk.agent.llm.stream_pipe import stream_pipeline
from mobile_use_sdk.agent.memory.messages import AgentMessages
from mobile_use_sdk.config import LLMConfig

from .llm import LLM


class DoubaoLLM(LLM):
    temperature = 0.0

    def __init__(self, llm_config: LLMConfig | None = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

        if llm_config is None:
            llm_config = LLMConfig()

        self.model_name = llm_config.model
        self.base_url = llm_config.base_url
        self.api_key = llm_config.api_key

        # self.llm = ChatOpenAI(
        #     api_key=self.api_key,
        #     base_url=self.base_url,
        #     model=self.model_name,
        #     streaming=is_stream,
        #     temperature=self.temperature,
        #     stream_usage=True,
        # )
        self.llm = ChatDeepSeek(
            api_key=self.api_key,
            api_base=self.base_url,
            model_name=self.model_name,
            temperature=self.temperature,
        )

    async def async_chat(self, messages: list[BaseMessage], is_stream: bool = False) -> tuple[str, str, str, str]:
        """调用模型并处理重试逻辑."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                chunk_id, content, summary, tool_call = await self._invoke_model(messages, is_stream)

                return chunk_id, content, summary, tool_call

            except asyncio.CancelledError:
                # cancel 不处理，直接向外抛出
                raise

            except Exception as e:
                retry_count += 1
                self.logger.exception(f"模型调用失败，重试第 {retry_count} 次。错误: {e}")

                if retry_count >= max_retries:
                    raise

                await asyncio.sleep(1)
        return None

    async def _invoke_model(self, messages: list[BaseMessage], is_stream: bool = False) -> tuple[str, str, str]:
        if is_stream:
            return await self._invoke_stream_model(messages)
        return await self._invoke_sync_model(messages)

    async def _invoke_stream_model(self, messages: list[BaseMessage]) -> tuple[str, str, str]:
        response = await self.llm.ainvoke(messages)
        # Langgraph 会监听 langchain invoke 的内容，在 graph.astream 外处理 pipe
        content, summary, tool_call = stream_pipeline.complete(id=response.id)

        return response.id, content, summary, tool_call

    async def _invoke_sync_model(self, messages: list[BaseMessage]) -> tuple[str, str, str]:
        use_openai_client = False
        # Ark Api 在 Langchain 下拿不到 token usage
        if use_openai_client:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=AgentMessages.convert_langchain_to_openai_messages(messages),
                temperature=self.temperature,
            )
            content = response.choices[0].message.content
            # output_tokens = response.usage.completion_tokens
            # input_tokens = response.usage.prompt_tokens

        else:
            response = await self.llm.ainvoke(messages)
            content = response.content
            # reasoning_content = response.additional_kwargs.get("reasoning_content", "")
        stream_pipeline.pipe(id=response.id, delta=content)
        content, summary, tool_call = stream_pipeline.complete(id=response.id)

        return response.id, content, summary, tool_call

    async def invoke(self, messages: list[BaseMessage]) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content
