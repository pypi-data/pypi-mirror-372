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

from langchain_core.messages import SystemMessage
from langgraph.config import get_stream_writer

from mobile_use_sdk.agent.graph.sse_output import (
    get_writer_workflow_tool_input,
    get_writer_workflow_tool_output,
)
from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.infra.model import ToolCall
from mobile_use_sdk.agent.prompt.doubao_vision_pro import seed_markdown_system_prompt
from mobile_use_sdk.agent.tools.tools import Tools
from mobile_use_sdk.mobile import Mobile

logger = logging.getLogger(__name__)


def prepare_node(mobile: Mobile, tools: Tools, additional_system_prompt: str):
    """创建准备节点的闭包工厂函数.

    Args:
        mobile: 移动端客户端实例

    Returns:
        prepare_node函数
    """

    async def prepare_node_impl(state: MobileUseAgentState):
        """准备节点 - 初始化消息上下文和初始任务信息.

        这个节点负责在Agent执行开始前初始化消息上下文，
        获取手机APP列表信息，并创建初始任务消息。
        这是整个Agent流程的第一个节点。

        Args:
            state: 当前Agent状态

        Returns:
            MobileUseAgentState: 更新后的状态，包含初始消息和APP列表
        """
        sse_writer = get_stream_writer()
        messages = state.get("messages", [])
        # screenshots = state.get("screenshots", [])

        # 仅当第一次执行图时才添加系统消息
        if len(messages) == 0:
            messages.append(
                SystemMessage(
                    content=seed_markdown_system_prompt(
                        tools.list_inner_tools_prompt_string(),
                        tools.list_mobile_tools_prompt_string(),
                        tools.list_mcp_tools_prompt_string(),
                        additional_system_prompt,
                    ),
                    id=str(uuid.uuid4()),
                )
            )

        # 获取手机APP列表信息
        app_list = []
        if hasattr(mobile, "list_apps") and callable(mobile.list_apps):
            # 创建工具调用信息用于SSE消息
            tool_call: ToolCall = {"name": "list_apps", "arguments": {}}

            # 发送工作流工具调用开始消息
            tool_input_message = get_writer_workflow_tool_input(state, tool_call)
            if tool_input_message:
                sse_writer(tool_input_message)

            try:
                app_list = await mobile.list_apps()

                # 创建包含应用名称列表的输出消息
                if app_list:
                    app_names = [app.get("app_name", "Unknown") for app in app_list]
                    tool_output_content = f"Found {len(app_list)} apps: {', '.join(app_names)}"
                else:
                    tool_output_content = "No apps found"

                # 发送工作流工具调用成功消息
                tool_output_message = get_writer_workflow_tool_output(state, tool_call, tool_output_content, "success")
                if tool_output_message:
                    sse_writer(tool_output_message)

            except Exception as e:
                logger.warning(f"获取应用列表失败，使用空列表: {e!s}")
                app_list = []

                # 发送工作流工具调用失败消息
                tool_output_message = get_writer_workflow_tool_output(
                    state, tool_call, f"Failed to get app list: {e!s}", "stop"
                )
                if tool_output_message:
                    sse_writer(tool_output_message)

        return {"messages": messages, "init_app_list": app_list}

    return prepare_node_impl
