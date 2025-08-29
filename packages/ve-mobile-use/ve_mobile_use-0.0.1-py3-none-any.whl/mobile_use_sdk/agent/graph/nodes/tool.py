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

from langgraph.config import get_stream_writer
from langgraph.errors import GraphInterrupt

from mobile_use_sdk.agent.graph.sse_output import (
    format_sse,
    get_writer_tool_input,
    get_writer_tool_output,
)
from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.tools import Tools
from mobile_use_sdk.agent.utils.safe_get import safe_get

logger = logging.getLogger(__name__)


def tool_node(tools: Tools):
    """创建工具执行节点的闭包工厂函数.

    Args:
        tools: 工具集合实例

    Returns:
        tool_node函数
    """

    async def tool_node_impl(state: MobileUseAgentState) -> MobileUseAgentState:
        """工具执行节点 - 执行工具调用.

        这个节点负责执行从语言模型生成的工具调用，
        包括特殊工具和常规工具的执行，并处理执行结果。

        Args:
            state: 当前Agent状态

        Returns:
            MobileUseAgentState: 更新后的状态，包含工具执行结果
        """
        sse_writer = get_stream_writer()

        # 获取最新的工具调用（数组中的最后一个）
        tool_calls = state.get("tool_calls", [])
        if not tool_calls:
            raise ValueError("No tool calls found in state")
        latest_tool_call_record = tool_calls[-1]
        tool_call = latest_tool_call_record.get("tool_call")
        tool_name = tool_call.get("name")

        logger.info(f"tool_call========: {tool_call}")

        # 特殊工具
        if tools.is_special_tool(tool_name):
            try:
                content = await tools.exec(tool_call)
                # Human Interrupt 特殊处理，某些工具不需要输出 SSE 消息
                if not tools.is_omit_sse_output(tool_name):
                    sse_writer(format_sse(tools.get_special_message(tool_name, content, state)))

                latest_tool_call_record["tool_output"] = tools.get_special_memory(tool_name, content)
                state.update(tool_calls=tool_calls)
            # Human Interrupt 特殊处理
            except GraphInterrupt as e:
                web_output = safe_get(e, "args.0.0.value.request_user", "请您给更多的提示，让我接着运行")
                sse_writer(format_sse(tools.get_special_message(tool_name, web_output, state)))
                # 这个错误会被 langgraph 捕获，但不会接着在 astream 中抛出
                raise
            except Exception as e:
                logger.exception(f"special_tool_call Error: ({tool_name}) {e}")
                raise
            return state

        # 写工具 input
        sse_writer(get_writer_tool_input(state, tool_call))

        try:
            result = await tools.exec(tool_call)
            memory_result = f"{tool_name}:({tool_call.get('arguments', {})})\n{result}\n操作下发成功"
            output = {"result": memory_result}
            latest_tool_call_record["tool_output"] = output

            # 新增：保存工具输出到state，供下次model节点使用
            state.update(
                tool_calls=tool_calls,
                last_tool_output=memory_result,  # 保存纯文本工具输出
            )

        except Exception as e:
            logger.exception(f"tool_call_client.call error: {e}")
            result = f"Error: {e!s}"
            sse_writer(get_writer_tool_output(state, tool_call, result, status="stop"))
            # 更新最新的工具调用记录，添加错误输出
            latest_tool_call_record["tool_output"] = {"result": result}
            state.update(
                tool_calls=tool_calls,
                last_tool_output=f"Error: {e!s}",  # 保存错误信息
            )

        logger.info(f"tool_output========: {output if 'output' in locals() else result}")

        # 写工具 output
        sse_writer(get_writer_tool_output(state, tool_call, result, status="success"))

        return state

    return tool_node_impl
