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

import logging
import uuid

from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

from mobile_use_sdk.agent.graph.sse_output import get_writer_think
from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.llm.llm import LLM
from mobile_use_sdk.agent.prompt.human_prompt import (
    build_messages_with_screenshots,
    get_human_message_without_screenshot,
)
from mobile_use_sdk.agent.tools.action_parser import ActionParser

logger = logging.getLogger(__name__)


def model_node(llm: LLM):
    """创建模型节点的闭包工厂函数.

    Args:
        llm: 语言模型实例

    Returns:
        model_node函数
    """

    async def model_node_impl(state: MobileUseAgentState) -> MobileUseAgentState:
        """大模型节点 - 根据当前状态计算行动和工具调用.

        Args:
            state: 当前Agent状态

        Returns:
            MobileUseAgentState: 更新后的状态，包含工具调用信息
        """
        iteration_count = state.get("iteration_count", 0)
        is_stream = state.get("is_stream")
        messages = list(state.get("messages", []))

        # 🚀 创建纯文本消息
        text_human_message = get_human_message_without_screenshot(state)

        # 🚀 如果有当前截图，从截图中获取ID并关联到消息
        current_screenshot = state.get("current_screenshot")
        if current_screenshot:
            screenshot_id = current_screenshot.get("id")

            # 在消息的 additional_kwargs 中存储截图ID
            text_human_message.additional_kwargs["screenshot_id"] = screenshot_id

        # 🚀 构建发送给LLM的消息列表：创建新数组副本，不修改原数组
        temp_messages = [*messages, text_human_message]  # 创建新数组

        # 获取截图字典
        screenshots_dict = state.get("screenshots", {})

        messages_for_llm = build_messages_with_screenshots(
            temp_messages, screenshots_dict, state.get("keep_last_n_screenshots")
        )

        # 调用模型
        chunk_id, content, summary, tool_call = await llm.async_chat(messages_for_llm, is_stream)

        logger.info(f"content========: {content}")

        if not is_stream:
            # 非流式传输直接输出对应的summary
            sse_writer = get_stream_writer()
            sse_writer(get_writer_think(state, chunk_id, summary))

        # 🚀 创建AI消息
        ai_message = AIMessage(role="assistant", content=content)

        # 🚀 创建新的messages数组用于保存到state
        updated_messages = [*messages, text_human_message, ai_message]

        # 解析工具调用
        parsed_tool_call = ActionParser.parse_tool_call_string(tool_call)
        if parsed_tool_call is None:
            parsed_tool_call = {
                "name": "error_action",
                "arguments": {"content": content},
            }

        # 创建新的工具调用记录
        tool_calls = state.get("tool_calls", [])
        tool_call_id = str(uuid.uuid4())
        tool_calls.append(
            {
                "tool_call": parsed_tool_call,
                "tool_output": None,
                "id": tool_call_id,
                "tool_name": parsed_tool_call.get("name", ""),
            }
        )

        # 构建返回的状态
        return {
            "tool_calls": tool_calls,
            "current_tool_call_id": tool_call_id,
            "iteration_count": iteration_count + 1,
            "chunk_id": chunk_id,
            "messages": updated_messages,
            "last_tool_output": None,  # 清除上次的工具输出
        }

    return model_node_impl
