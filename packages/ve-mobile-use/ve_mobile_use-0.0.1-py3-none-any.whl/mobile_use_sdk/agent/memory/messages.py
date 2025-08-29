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

import json

from langchain_core.messages import BaseMessage


class AgentMessages:
    def __init__(self, messages: list[BaseMessage]) -> None:
        self._messages: list[BaseMessage] = messages

    def get_messages(self):
        return self._messages

    def length(self):
        return len(self._messages)

    def index(self, index: int) -> BaseMessage:
        if self._messages and 0 <= index < self.length():
            return self._messages[index]
        raise IndexError(f"消息索引 {index} 超出范围")

    def append(self, message: BaseMessage) -> None:
        self._messages.append(message)

    def replace(self, idx, message) -> None:
        if 0 <= idx < len(self._messages):
            self._messages[idx] = message
        else:
            raise IndexError(f"消息索引 {idx} 超出范围")

    def insert(self, idx, message) -> None:
        if 0 <= idx <= len(self._messages):
            self._messages.insert(idx, message)
        else:
            raise IndexError(f"插入索引 {idx} 超出范围")

    def replace_all(self, messages) -> None:
        self._messages = messages

    @staticmethod
    def convert_langchain_to_openai_messages(
        messages: list[BaseMessage],
    ) -> list[dict]:
        """将 LangChain messages 转换为 OpenAI 格式."""
        openai_messages = []

        for msg in messages:
            if msg.type == "human":
                role = "user"
            elif msg.type == "ai":
                role = "assistant"
            elif msg.type == "system":
                role = "system"
            elif msg.type == "tool":
                role = "tool"
            elif msg.type == "function":
                role = "function"
            else:
                role = msg.type  # 兜底

            message_dict = {"role": role, "content": msg.content}

            # 处理工具调用（如果是 AIMessage）
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                message_dict["tool_calls"] = []
                for tool_call in msg.tool_calls:
                    message_dict["tool_calls"].append(
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": json.dumps(tool_call["args"]),
                            },
                        }
                    )

            # 处理工具消息的 tool_call_id
            if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id

            openai_messages.append(message_dict)

        return openai_messages
