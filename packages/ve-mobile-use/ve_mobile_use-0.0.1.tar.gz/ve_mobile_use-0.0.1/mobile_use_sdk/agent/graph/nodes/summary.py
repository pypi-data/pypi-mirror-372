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
import logging

from langchain_core.messages import SystemMessage

from mobile_use_sdk.agent.utils.messages import get_human_message

logger = logging.getLogger(__name__)


async def summary_node(
    llm,
    output_format: type,
    user_prompt: str,
    iteration_count: int,
    final_tool_call: dict,
    final_tool_output: str,
    messages: list,
) -> dict:
    """生成结构化摘要 - 创建任务执行的结构化总结.

    这个函数负责生成任务执行的结构化总结，将对话历史和执行结果
    格式化为指定的Pydantic模型格式。

    Args:
        llm: 语言模型实例
        thread_id: 线程ID用于获取上下文
        output_format: 输出的Pydantic模型类
        user_prompt: 用户查询
        iteration_count: 迭代次数
        final_tool_call: 最终工具调用信息
        final_tool_output: 最终工具输出
        messages: 消息列表

    Returns:
        dict: 结构化总结数据
    """
    # 获取所有消息并格式化为字符串
    formatted_messages = []
    for idx, msg in enumerate(messages):
        msg_type = msg.type if hasattr(msg, "type") else str(type(msg))
        if hasattr(msg, "content"):
            if isinstance(msg.content, list):
                # 处理包含图片的消息
                text_parts = []
                for part in msg.content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            text_parts.append("[图片]")
                    else:
                        text_parts.append(str(part))
                content = " ".join(text_parts)
            else:
                content = str(msg.content)
        else:
            content = str(msg)

        formatted_messages.append(f"{idx + 1}. [{msg_type}] {content}")

    all_messages_text = "\n".join(formatted_messages)

    try:
        # 获取 schema 信息
        schema_json = output_format.model_json_schema()

        # 构建提示词
        structured_prompt = f"""
基于以下任务执行信息，请生成符合指定 JSON schema 的结构化输出。

用户信息：
- 查询：{user_prompt}
- 执行步骤：{iteration_count} 步
- 最终工具调用：{final_tool_call}
- 工具输出：{final_tool_output}

完整对话历史：
{all_messages_text}

请严格按照以下 JSON schema 格式生成输出：

```json
{schema_json}
```

注意：
1. 不要生成 markdown，只生成纯 json 字符串
2. 确保所有字段都符合 schema 要求
3. 提供详细且准确的信息
4. 使用中文或英文根据内容适当选择
5. 不要包含 schema 中未定义的字段

请只返回符合 schema 的 JSON 数据，不要包含其他解释。
"""

        # 使用传入的 LLM 实例生成结构化输出
        # 直接传递is_stream=False参数给invoke方法

        # 调用 LLM 的 invoke 函数直接生成结构化输出
        response = await llm.invoke(
            [
                SystemMessage(content="你是一个专业的数据提取助手，请严格按照给定的 JSON schema 格式生成结构化输出。"),
                get_human_message(user_content=structured_prompt),
            ]
        )

        # 解析响应为指定 schema
        if response and len(response) > 0:
            try:
                # 尝试解析 JSON
                parsed_data = json.loads(response)
                model_instance = output_format(**parsed_data)
                return model_instance.model_dump()
            except (json.JSONDecodeError, Exception) as e:
                error_msg = f"Failed to parse structured output: {e}"
                logger.exception(error_msg)
                # 抛出异常而不是返回假数据
                raise ValueError(error_msg)
        else:
            error_msg = "No response generated for structured output"
            logger.error(error_msg)
            # 抛出异常而不是返回假数据
            raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Failed to generate structured output: {e}"
        logger.exception(error_msg)
        # 重新抛出异常而不是返回假数据
        raise ValueError(error_msg)
