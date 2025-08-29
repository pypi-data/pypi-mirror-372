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

from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.tools import Tools

logger = logging.getLogger(__name__)


def should_react_continue(tools: Tools):
    """创建反应继续条件的闭包工厂函数.

    Args:
        tools: 工具集合实例

    Returns:
        should_react_continue函数
    """

    async def should_react_continue_impl(state: MobileUseAgentState) -> str:
        """反应继续条件 - 决定是否继续执行Agent流程.

        这个条件边函数用于判断Agent是否应该继续执行下一个迭代，
        基于迭代次数和工具类型等因素做出决策。

        Args:
            state: 当前Agent状态

        Returns:
            str: 决策结果 - "finish" 或 "continue"
        """
        # 检查是否达到最大迭代次数
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get(
            "max_iterations",
        )

        # 获取最新的工具调用（数组中的最后一个）
        tool_calls = state.get("tool_calls", [])
        if not tool_calls:
            # 如果没有工具调用，继续执行
            return "continue"
        latest_tool_call_record = tool_calls[-1]
        tool_call = latest_tool_call_record.get("tool_call")
        tool_name = tool_call.get("name")

        if tools.is_special_tool(tool_name) and tool_name != "request_user":
            return "finish"

        if iteration_count >= max_iterations:
            return "finish"

        # 否则继续执行
        return "continue"

    return should_react_continue_impl
