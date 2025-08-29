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

from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage

from mobile_use_sdk.config import LLMConfig


class LLM(ABC):
    """抽象LLM基类，定义所有LLM实现必须遵循的接口."""

    model_name: str
    base_url: str
    api_key: str

    @abstractmethod
    def __init__(self, llm_config: LLMConfig | None = None) -> None:
        """初始化LLM实例."""
        pass

    @abstractmethod
    async def async_chat(
        self,
        messages: list[BaseMessage],
        is_stream: bool = False,
        system_prompt: BaseMessage = None,
    ) -> tuple[str, str, str, str]:
        """异步聊天方法.

        Args:
            messages: 消息列表
            is_stream: 是否流式传输

        Returns:
            tuple: (chunk_id, content, summary, tool_call)
        """
        pass

    @abstractmethod
    async def invoke(self, messages: list[BaseMessage]) -> str:
        """直接调用模型的invoke函数.

        Args:
            messages: 消息列表

        Returns:
            str: 模型响应内容
        """
        pass
