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
import uuid
from typing import Literal

from pydantic import BaseModel

from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.infra.message_web import (
    SSEReasoningMessageData,
    SSEThinkMessageData,
    SSEToolCallMessageData,
    SSEWorkflowToolMessageData,
)
from mobile_use_sdk.agent.infra.model import ToolCall
from mobile_use_sdk.agent.llm.stream_pipe import stream_pipeline


def format_sse(data: dict | BaseModel | None = None, **kwargs) -> str:
    if isinstance(data, BaseModel):
        data = data.model_dump()
    else:
        if not data:
            data = {}
        data.update(kwargs)
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_messages(update, is_stream: bool, task_id: str):
    # 处理字符串类型的消息（GUI代理返回的SSE格式消息）
    if isinstance(update, str) and update.startswith("data: "):
        # 直接返回已经格式化好的SSE消息
        yield update
        return

    eventType = update[0]
    if eventType == "custom":
        yield update[1]
        return
    elif eventType == "messages":
        if not is_stream:
            return
        if isinstance(update, tuple) and len(update) == 2:
            _, data = update
            message_chunk, metadata = data
            if metadata.get("langgraph_node") == "model" and message_chunk.type == "AIMessageChunk":
                # 深度思考内容
                reasoning_content = message_chunk.additional_kwargs.get("reasoning_content", "")
                if reasoning_content:
                    yield format_sse(
                        SSEReasoningMessageData(
                            id=message_chunk.id,
                            task_id=task_id,
                            content=reasoning_content,
                        )
                    )
                # content 内容
                if message_chunk.content:
                    pipe_result = stream_pipeline.pipe(
                        id=message_chunk.id,
                        delta=message_chunk.content,
                    )
                    if not pipe_result:
                        return
                    (id, delta) = pipe_result
                    if not delta:
                        return
                    yield format_sse(
                        SSEThinkMessageData(
                            id=id,
                            task_id=task_id,
                            role="assistant",
                            type="think",
                            content=delta,
                        )
                    )
            return
    else:
        yield f"Unknown event type: {eventType}"


def get_writer_tool_input(state: MobileUseAgentState, tool_call: ToolCall):
    state.update(current_tool_call_id=str(uuid.uuid4()))
    return format_sse(
        SSEToolCallMessageData(
            id=state.get("chunk_id"),
            task_id=state.get("task_id"),
            tool_id=state.get("current_tool_call_id"),
            type="tool",
            tool_type="tool_input",
            tool_name=tool_call.get("name", ""),
            tool_input=json.dumps(tool_call.get("arguments", {}), ensure_ascii=False),
            status="start",
        )
    )


def get_writer_tool_output(
    state: MobileUseAgentState,
    tool_call: ToolCall,
    tool_output: str,
    status: Literal["start", "stop", "success"],
):
    current_tool_call_id = state.get("current_tool_call_id")
    if current_tool_call_id:
        state.update(current_tool_call_id="")

        return format_sse(
            SSEToolCallMessageData(
                id=state.get("chunk_id"),
                task_id=state.get("task_id"),
                tool_id=current_tool_call_id,
                type="tool",
                tool_type="tool_output",
                tool_name=tool_call.get("name", ""),
                tool_input=json.dumps(tool_call.get("arguments", {}), ensure_ascii=False),
                tool_output=tool_output,
                status=status,
            )
        )
    return None


def get_writer_think(state: MobileUseAgentState, chunk_id: str, summary: str):
    return format_sse(
        SSEThinkMessageData(
            id=chunk_id,
            task_id=state.get("task_id"),
            role="assistant",
            type="think",
            content=summary,
        )
    )


def get_writer_workflow_tool_input(state: MobileUseAgentState, tool_call: ToolCall):
    """生成工作流工具调用输入消息，用于主动调用的工具（如初始化截图、应用列表等）."""
    chunk_id = state.get("chunk_id")
    if not chunk_id:
        chunk_id = str(uuid.uuid4())
    state.update(current_tool_call_id=str(uuid.uuid4()), chunk_id=chunk_id)
    return format_sse(
        SSEWorkflowToolMessageData(
            id=state.get("chunk_id"),
            task_id=state.get("task_id"),
            tool_id=state.get("current_tool_call_id"),
            type="workflow_tool",
            tool_type="tool_input",
            tool_name=tool_call.get("name", ""),
            tool_input=json.dumps(tool_call.get("arguments", {}), ensure_ascii=False),
            status="start",
        )
    )


def get_writer_workflow_tool_output(
    state: MobileUseAgentState,
    tool_call: ToolCall,
    tool_output: str,
    status: Literal["start", "stop", "success"],
):
    """生成工作流工具调用输出消息，用于主动调用的工具（如初始化截图、应用列表等）."""
    current_tool_call_id = state.get("current_tool_call_id")
    if current_tool_call_id:
        state.update(current_tool_call_id="")

        return format_sse(
            SSEWorkflowToolMessageData(
                id=state.get("chunk_id"),
                task_id=state.get("task_id"),
                tool_id=current_tool_call_id,
                type="workflow_tool",
                tool_type="tool_output",
                tool_name=tool_call.get("name", ""),
                tool_input=json.dumps(tool_call.get("arguments", {}), ensure_ascii=False),
                tool_output=tool_output,
                status=status,
            )
        )
    return None
