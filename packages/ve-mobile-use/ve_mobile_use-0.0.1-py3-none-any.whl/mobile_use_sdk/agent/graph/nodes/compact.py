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

from langchain_core.messages import AIMessage, SystemMessage

from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.llm.ark_token import ArkTokenCounter
from mobile_use_sdk.agent.llm.llm import LLM
from mobile_use_sdk.agent.prompt.human_prompt import build_messages_with_screenshots
from mobile_use_sdk.agent.prompt.summary import summary_system_prompt
from mobile_use_sdk.agent.utils.messages import get_human_message
from mobile_use_sdk.config.config import LLMConfig

logger = logging.getLogger(__name__)


def extract_text_and_images_for_token_counting(state: MobileUseAgentState):
    """从消息中提取文本和图片信息，用于token计算.

    Args:
        messages_to_summarize: 需要处理的消息列表
        state: Agent状态，包含截图数据和分辨率信息

    Returns:
        tuple: (text, image_numbers, image_size)
            - text: str - 所有文本内容的连接
            - image_numbers: int - 图片数量
            - image_size: tuple[int, int] | None - 图片尺寸 (width, height)
    """
    all_texts = []
    image_count = 0
    image_size = None

    # 获取截图数据，用于获取分辨率
    current_screenshot = state.get("current_screenshot", None)
    messages = list(state.get("messages", []))
    real_messages = build_messages_with_screenshots(
        messages=messages,
        screenshots_dict=state.get("screenshots", {}),
        keep_last_n=state.get("keep_last_n_screenshots"),
    )

    for msg in real_messages:
        if not hasattr(msg, "content"):
            continue

        # 处理纯文本消息
        if not isinstance(msg.content, list):
            text_content = str(msg.content)
            if text_content:
                all_texts.append(text_content)
            continue

        # 处理包含图片的消息（数组格式）
        for part in msg.content:
            if not isinstance(part, dict):
                continue

            part_type = part.get("type")
            if part_type == "text":
                text_content = part.get("text", "")
                if text_content:
                    all_texts.append(text_content)
            elif part_type == "image_url":
                image_count += 1

    # 连接所有文本内容
    combined_text = "\n".join(all_texts)

    # 先用最后一张截图的分辨率
    if current_screenshot:
        image_size = current_screenshot.get("screenshot_dimensions")

    messages_to_summarize = real_messages[1:]

    return combined_text, image_count, image_size, messages_to_summarize


def create_summary_message(content: str):
    return AIMessage(
        content=f"""
---
到目前为止执行的动作总结:
{content}
---
"""
    )


async def generate_summary(llm: LLM, messages_to_summarize, last_screenshot_url: str, last_tool_output: str):
    """使用LLM生成消息总结."""
    try:
        return await llm.invoke(
            [
                SystemMessage(content=summary_system_prompt),
                *messages_to_summarize,
                get_human_message(
                    user_content=f"""\n上面是所有的对话历史，这是最后一张截图，请根据截图，最后一次工具输出和对话历史，对之前执行的动作做一个总结。\n\n这里最后一次工具执行的输出：\n{last_tool_output}\n""",
                    url=last_screenshot_url,
                ),
            ]
        )
    except Exception as e:
        logger.exception(f"Summary failed: {e}")
        return None


def compact_node(llm: LLM):
    """创建消息压缩节点的闭包工厂函数.

    Args:
        llm: 语言模型实例

    Returns:
        compact_node函数
    """

    async def compact_node_impl(state: MobileUseAgentState) -> MobileUseAgentState:
        """消息压缩节点 - 压缩消息历史以减少上下文长度.

        这个节点负责在工具执行后压缩消息历史，
        使用LLM生成总结来替代过长的对话历史。

        Args:
            state: 当前Agent状态

        Returns:
            MobileUseAgentState: 更新后的状态，包含压缩后的消息
        """
        # 获取当前消息
        messages = state.get("messages", [])

        current_screenshot = state.get("current_screenshot", None)

        last_tool_output = state.get("last_tool_output", None)

        # 提取文本和图片内容用于token计算
        text, image_numbers, image_size, messages_to_summarize = extract_text_and_images_for_token_counting(state)

        # 创建token计数器并传递提取的参数
        ark_token_counter = ArkTokenCounter(
            llm_config=LLMConfig(model=llm.model_name, base_url=llm.base_url, api_key=llm.api_key)
        )

        # 使用提取的参数检查token是否超出限制
        is_token_exceeded = await ark_token_counter.is_token_exceed(
            text=text, image_numbers=image_numbers, image_size=image_size
        )
        if not is_token_exceeded:
            return None

        summary_message = await generate_summary(
            llm,
            messages_to_summarize,
            last_screenshot_url=current_screenshot.get("screenshot", ""),
            last_tool_output=last_tool_output,
        )

        # TODO 这里需要优化，如果用户多轮对话，需要重点总结过往的每一段对话的历史，和突出用户最新的任务
        if summary_message:
            # 保留系统提示词，和第一条 HumanMessage，组装成 system_prompt -> 最初任务的 HumanMessage -> 总结消息
            keep_messages = messages[:2]

            # 新的消息列表：系统消息 + 总结消息
            compressed_messages = [*keep_messages, create_summary_message(summary_message)]

            logger.info(f"Messages compressed with summary from {len(messages)} to {len(compressed_messages)}")

            return {"messages": compressed_messages, "current_screenshot": None}

        return None

    return compact_node_impl
