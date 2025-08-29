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

from langgraph.types import interrupt

from mobile_use_sdk.agent.infra.message_web import (
    SSEUserInterruptMessageData,
)
from mobile_use_sdk.agent.tools.tool.abc import SpecialTool


class RequestUserTool(SpecialTool):
    def __init__(self) -> None:
        super().__init__(
            name="request_user",
            description="When the task is unsolvable or you need the user's help like login, input verification code or need more information, call the user. You must exactly describe the user request in content.",
            parameters={
                "type": "object",
                "required": ["content"],
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to call the user",
                    },
                },
            },
        )

    async def handler(self, args: dict) -> str:
        request_user_content = args.get("content")
        user_response = interrupt({"request_user": request_user_content})
        query = user_response.get("query", "")
        return f"用户回复: {query}"

    def special_message(self, content: str, args: dict):
        return SSEUserInterruptMessageData(
            id=args.get("chunk_id"),
            task_id=args.get("task_id"),
            role="assistant",
            type="user_interrupt",
            interrupt_type="text",
            content=content,
        )

    def special_memory(self, content: str = ""):
        return content
