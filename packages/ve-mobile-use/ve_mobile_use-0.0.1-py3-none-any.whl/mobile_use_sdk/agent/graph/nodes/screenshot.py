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
import uuid

from langgraph.config import get_stream_writer

from mobile_use_sdk.agent.graph.sse_output import (
    get_writer_workflow_tool_input,
    get_writer_workflow_tool_output,
)
from mobile_use_sdk.agent.graph.state import MobileUseAgentState, ScreenshotData
from mobile_use_sdk.agent.infra.model import ToolCall
from mobile_use_sdk.mobile import Mobile

logger = logging.getLogger(__name__)


def screenshot_node(mobile: Mobile):
    """创建截图节点的闭包工厂函数.

    Args:
        mobile: 移动端客户端实例

    Returns:
        screenshot_node函数
    """

    async def screenshot_node_impl(state: MobileUseAgentState) -> dict:
        """截图节点 - 获取设备屏幕截图.

        Args:
            state: 当前Agent状态

        Returns:
            dict: 包含更新的状态字段的新字典
        """
        sse_writer = get_stream_writer()
        iteration_count = state.get("iteration_count")

        # 获取截图
        if iteration_count > 0:
            # 等待 UI 操作完成
            await asyncio.sleep(state.get("step_interval"))

        # 创建工具调用信息用于SSE消息
        tool_call: ToolCall = {"name": "screenshot", "arguments": {}}

        # 发送工作流工具调用开始消息
        tool_input_message = get_writer_workflow_tool_input(state, tool_call)
        if tool_input_message:
            sse_writer(tool_input_message)

        try:
            screenshot_state = await mobile.screenshot()
            screenshot = screenshot_state.get("screenshot")
            screenshot_dimensions = screenshot_state.get("screenshot_dimensions")

            logger.info(f"Screenshot taken: {screenshot}")
            logger.info(f"Screenshot dimensions: {screenshot_dimensions}")

            # 发送工作流工具调用成功消息
            tool_output_message = get_writer_workflow_tool_output(state, tool_call, f"{screenshot}", "success")
            if tool_output_message:
                sse_writer(tool_output_message)

        except Exception as e:
            logger.exception(f"Screenshot failed: {e!s}")
            # 发送工作流工具调用失败消息
            tool_output_message = get_writer_workflow_tool_output(state, tool_call, f"Screenshot failed: {e!s}", "stop")
            if tool_output_message:
                sse_writer(tool_output_message)
            raise

        # 🚀 为截图生成唯一ID
        screenshot_id = str(uuid.uuid4())

        # 创建新的截图数据对象
        screenshot_data = ScreenshotData(
            screenshot=screenshot, screenshot_dimensions=screenshot_dimensions, id=screenshot_id
        )

        # 🚀 更新截图字典（新的存储方式）
        screenshots_dict = dict(state.get("screenshots", {}))
        screenshots_dict[screenshot_id] = screenshot_data

        # 核心优化：只更新当前截图，不操作messages
        return {
            "screenshots": screenshots_dict,  # 使用字典存储
            "current_screenshot": screenshot_data,  # 包含ID的截图数据
        }

    return screenshot_node_impl
