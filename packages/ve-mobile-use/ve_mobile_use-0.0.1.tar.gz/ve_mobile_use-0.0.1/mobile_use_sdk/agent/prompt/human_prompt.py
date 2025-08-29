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

"""截图相关的提示词生成函数.

这个模块包含了用于生成包含截图的用户消息的函数。
"""

import logging
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage

from mobile_use_sdk.agent.graph.state import ScreenshotData
from mobile_use_sdk.agent.utils.messages import get_human_message

logger = logging.getLogger(__name__)


# def create_initial_message_with_screenshot(
#     user_prompt: str,
#     app_list: str,
#     screenshot: str,
#     screenshot_dimensions: Tuple[int, int],
# ) -> HumanMessage:
#     user_content = f"""
# 当前时间点 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# {f"手机初始化APP列表信息:\n```\n{app_list}\n```" if app_list else ""}
# 用户对你说: {user_prompt}
# """

#     # 添加截图信息
#     if screenshot and screenshot_dimensions:
#         user_content += f"""
# 请观察截图， 当前截图分辨率为 {screenshot_dimensions[0]}x{screenshot_dimensions[1]}"""

#     return get_human_message(url=screenshot, user_content=user_content)

# def create_iteration_message_with_screenshot(
#     user_prompt: str,
#     iteration_count: int,
#     tool_output: str,
#     screenshot_url: str,
#     screenshot_dimensions: tuple,
# ) -> HumanMessage:
#     """创建迭代中的用户消息"""
#     # 构建基础用户内容
#     user_content = f"""
# 当前轮次迭代次数 {iteration_count}
# 用户任务: {user_prompt}"""

#     # 如果有tool_output，则添加工具下发结果
#     if tool_output:
#         user_content += f"""
# 当前轮次工具下发结果:
# ```
# {tool_output}
# ```"""

#     # 添加截图信息
#     user_content += f"""
# 请观察截图， 当前截图分辨率为 {screenshot_dimensions[0]}x{screenshot_dimensions[1]}"""

#     return get_human_message(url=screenshot_url, user_content=user_content)

# def get_human_message_with_screenshot(state) -> HumanMessage:
#     """组装发送给LLM的完整用户消息（包含截图）"""
#     iteration_count = state.get("iteration_count", 0)
#     current_screenshot = state.get("current_screenshot")

#     if iteration_count == 0:
#         # 首次迭代：使用初始消息格式
#         app_list = state.get("init_app_list", [])

#         return create_initial_message_with_screenshot(
#             user_prompt=state.get("user_prompt", ""),
#             app_list=app_list,
#             screenshot=current_screenshot["screenshot"] if current_screenshot else "",
#             screenshot_dimensions=current_screenshot["screenshot_dimensions"] if current_screenshot else (0, 0),
#         )
#     else:
#         # 后续迭代：使用迭代消息格式
#         return create_iteration_message_with_screenshot(
#             user_prompt=state.get("user_prompt", ""),
#             iteration_count=iteration_count,
#             tool_output=state.get("last_tool_output", ""),
#             screenshot_url=current_screenshot["screenshot"] if current_screenshot else "",
#             screenshot_dimensions=current_screenshot["screenshot_dimensions"] if current_screenshot else (0, 0),
#         )


def create_initial_message_without_screenshot(
    user_prompt: str,
    app_list_str: str,
) -> HumanMessage:
    app_info = f"手机初始化APP列表信息:\n```\n{app_list_str}\n```" if app_list_str else ""
    user_content = f"""当前时间点 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{app_info}
用户对你说: {user_prompt}
"""

    return get_human_message(user_content=user_content)


def create_iteration_message_without_screenshot(
    user_prompt: str,
    iteration_count: int,
    tool_output: str | None = None,
) -> HumanMessage:
    """创建纯文本的用户消息（不包含截图）."""
    user_content = f"""当前轮次迭代次数 {iteration_count}
用户任务: {user_prompt}
"""

    # 如果有tool_output，则添加工具下发结果
    if tool_output:
        user_content += f"""
当前轮次工具下发结果:
```
{tool_output}
```"""

    # 关键：不传递url参数，创建纯文本消息
    return get_human_message(user_content=user_content)


def get_human_message_without_screenshot(state) -> HumanMessage:
    """创建存储到state的纯文本用户消息（不包含截图）."""
    iteration_count = state.get("iteration_count", 0)

    if iteration_count == 0:
        app_list = state.get("init_app_list", [])

        return create_initial_message_without_screenshot(
            app_list_str=app_list,
            user_prompt=state.get("user_prompt", ""),
        )
    # 后续迭代：使用现有的文本消息创建函数
    return create_iteration_message_without_screenshot(
        user_prompt=state.get("user_prompt", ""),
        iteration_count=iteration_count,
        tool_output=state.get("last_tool_output"),
    )


def build_messages_with_screenshots(
    messages: list[BaseMessage],
    screenshots_dict: dict[str, ScreenshotData],
    keep_last_n: int,
):
    """从后往前遍历消息，替换最后N条包含截图的消息."""
    result_messages = messages
    screenshots_added = 0

    # 从后往前遍历消息
    for i in range(len(result_messages) - 1, -1, -1):
        if screenshots_added >= keep_last_n:
            break

        message = result_messages[i]

        # 只处理human消息
        if hasattr(message, "type") and message.type == "human":
            # 从消息的 additional_kwargs 中获取截图ID
            screenshot_id = message.additional_kwargs.get("screenshot_id")

            if screenshot_id and screenshot_id in screenshots_dict:
                # 从截图字典中获取截图数据
                screenshot_data = screenshots_dict[screenshot_id]

                # 重新构建包含截图的消息
                enhanced_message = _enhance_message_with_screenshot(message, screenshot_data)
                result_messages[i] = enhanced_message
                screenshots_added += 1

                logger.info(
                    f"为消息（索引 {i}）添加截图ID {screenshot_id}，已添加 {screenshots_added}/{keep_last_n} 张截图"
                )

    return result_messages


def _enhance_message_with_screenshot(original_message, screenshot_data):
    """为消息添加截图信息."""
    # 导入这里放在函数内部，避免循环导入

    # 获取原始消息内容
    original_content = original_message.content if hasattr(original_message, "content") else str(original_message)

    # 为消息内容添加截图观察提示
    enhanced_content = f"{original_content}\n请观察截图，当前截图分辨率为 {screenshot_data['screenshot_dimensions'][0]}x{screenshot_data['screenshot_dimensions'][1]}"

    # 创建包含截图的新消息
    return get_human_message(url=screenshot_data["screenshot"], user_content=enhanced_content)
