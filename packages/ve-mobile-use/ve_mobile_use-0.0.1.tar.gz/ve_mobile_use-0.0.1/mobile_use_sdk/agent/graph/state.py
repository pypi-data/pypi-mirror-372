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

from collections.abc import Sequence
from typing import Any

from langgraph.graph.message import BaseMessage
from typing_extensions import TypedDict

from mobile_use_sdk.agent.infra.model import ToolCall


class ScreenshotData(TypedDict):
    """截图数据结构，包含截图URL和尺寸信息."""

    id: str
    screenshot: str  # 截图的url链接
    screenshot_dimensions: tuple[int, int]  # 截图的(宽度, 高度)信息


# 移除ScreenshotMessageMapping，改用WeakMap管理关联关系


class ToolCallRecord(TypedDict):
    """工具调用记录，包含工具调用和输出结果."""

    id: str
    tool_call: ToolCall  # MCP工具调用
    tool_output: dict[str, Any] | None  # 工具调用的输出结果
    tool_name: str  # 工具名称，与tool_call.name保持一致


class SharedState(TypedDict):
    messages: Sequence[BaseMessage]
    thread_id: str
    task_id: str
    chunk_id: str
    user_prompt: str
    is_stream: bool  # 是否流式输出
    iteration_count: int  # 当前迭代次数
    max_iterations: int  # 最大迭代次数


class ToolCallState(SharedState):
    tool_calls: list[ToolCallRecord]  # 工具调用记录数组
    current_tool_call_id: str


class MobileUseAgentState(ToolCallState):
    screenshots: dict[str, ScreenshotData]  # 截图字典，key是截图的唯一ID，value是截图数据
    current_screenshot: ScreenshotData | None  # 当前截图
    init_app_list: list[str] | None  # 初始化应用列表
    last_tool_output: str | None  # 上一次工具执行结果
    step_interval: float  # 因为手机 UI 有动画，所以需要等待一段时间
    output_format: Any | None  # 输出格式schema
    keep_last_n_screenshots: int  # 保留最后N张截图，默认1张
