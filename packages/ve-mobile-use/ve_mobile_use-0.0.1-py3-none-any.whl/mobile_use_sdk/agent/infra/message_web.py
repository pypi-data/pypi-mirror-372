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

from typing import Literal

from pydantic import BaseModel


class MessageMeta(BaseModel):
    finish_reason: str | None = None
    model: str | None = None
    prompt_tokens: int | None = None
    total_tokens: int | None = None


class SSEContentMessageData(BaseModel):
    id: str
    task_id: str
    role: str
    content: str
    response_meta: MessageMeta | None = None


class SSEReasoningMessageData(SSEContentMessageData):
    type: Literal["reasoning"] = "reasoning"
    role: Literal["assistant"] = "assistant"


class SSEThinkMessageData(SSEContentMessageData):
    type: Literal["think"] = "think"
    role: Literal["assistant"] = "assistant"


class SSEUserInterruptMessageData(SSEContentMessageData):
    type: Literal["user_interrupt"] = "user_interrupt"
    interrupt_type: Literal["text"]


class SSESummaryMessageData(SSEContentMessageData):
    type: Literal["summary"] = "summary"


class SSEToolCallMessageData(BaseModel):
    id: str
    task_id: str
    tool_id: str
    type: Literal["tool"] = "tool"
    status: Literal["start", "stop", "success"]
    tool_type: Literal["tool_input", "tool_output"]
    tool_name: str
    tool_input: str | None = None
    tool_output: str | None = None


class SSEWorkflowToolMessageData(BaseModel):
    """Workflow tool message for displaying subtle tool calls during initialization."""

    id: str
    task_id: str
    tool_id: str
    type: Literal["workflow_tool"] = "workflow_tool"
    status: Literal["start", "stop", "success"]
    tool_type: Literal["tool_input", "tool_output"]
    tool_name: str
    tool_input: str | None = None
    tool_output: str | None = None
