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

import uuid
from datetime import datetime

from langgraph.errors import GraphRecursionError
from langgraph.types import Command, RunnableConfig
from langsmith import traceable
from pydantic import BaseModel

from mobile_use_sdk.agent.graph.builder import create_mobile_use_agent
from mobile_use_sdk.agent.graph.nodes import summary_node
from mobile_use_sdk.agent.graph.sse_output import format_sse, stream_messages
from mobile_use_sdk.agent.history.history import (
    AgentHistory,
    AgentInfo,
    AgentResponse,
    AgentResult,
)
from mobile_use_sdk.agent.infra.message_web import SSESummaryMessageData
from mobile_use_sdk.agent.llm.doubao import DoubaoLLM
from mobile_use_sdk.agent.mcp_hub.global_connection_manager import mcp_manager
from mobile_use_sdk.agent.tools.tools import Tools
from mobile_use_sdk.config import AgentConfig, LLMConfig
from mobile_use_sdk.mobile.abc import Mobile

from .infra.logger import AgentLogger


class MobileUseAgent:
    name = "mobile_use"

    def __init__(
        self,
        llm_config: LLMConfig | None = None,
        agent_config: AgentConfig | None = None,
    ) -> None:
        self.logger = AgentLogger(__name__)
        self._initialized = False

        agent_config = agent_config or AgentConfig()
        self.llm_config = llm_config or LLMConfig()

        self.additional_system_prompt = agent_config.additional_system_prompt
        self.max_steps = agent_config.max_steps
        self.step_interval = agent_config.step_interval
        self.use_base64_screenshot = agent_config.use_base64_screenshot

        self.mcp_hub = None  # 将通过连接池获取
        self.mobile = None
        self.llm = None
        self.tools = None
        self.graph = None

    async def initialize(
        self,
        mobile: Mobile,
        mcp_json: dict | None = None,
    ):
        # 创建LLM实例并传入graph
        self.llm = DoubaoLLM(llm_config=self.llm_config)

        if mcp_json:
            # 只获取MCP连接（使用连接池）
            self.mcp_hub = await mcp_manager.get_mcp_hub(mcp_json)
            await self.mcp_hub.create_all_sessions()

        if mobile:
            # Mobile实例由外部工厂传入，Agent不关心连接管理
            self.mobile = mobile
            if hasattr(self.mobile, "change_config"):
                self.mobile.change_config(use_base64_screenshot=self.use_base64_screenshot)

        self.tools = await Tools.from_mcp(self.mcp_hub, self.mobile)
        self.graph = create_mobile_use_agent(self.llm, self.mobile, self.tools, self.additional_system_prompt)

        self._initialized = True
        return self

    @classmethod
    async def init_with_mobile(
        cls,
        mobile: Mobile,
        mcp_json: dict | None = None,
        llm_config: LLMConfig | None = None,
        agent_config: AgentConfig | None = None,
    ) -> "MobileUseAgent":
        # 创建实例
        instance = cls(llm_config=llm_config, agent_config=agent_config)

        # 初始化实例
        await instance.initialize(mobile=mobile, mcp_json=mcp_json)

        return instance

    def is_in_request_user(self, config: RunnableConfig) -> None:
        graph_state_values = self.graph.get_state(config=config).values
        return graph_state_values.get("tool_call", {}).get("name", "") == "request_user"

    def _prepare_graph_input(
        self,
        user_prompt: str,
        is_stream: bool,
        thread_id: str,
    ) -> tuple[dict, dict]:
        """准备图输入和配置的公共方法."""
        if not self._initialized:
            raise RuntimeError("Agent must be initialized before use. Call initialize() first.")

        self.logger.set_context(thread_id=thread_id)
        self.task_id = str(uuid.uuid4())

        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": self.max_steps * 3,
        }

        if self.is_in_request_user(config=config):
            graph_input = Command(resume={"query": user_prompt}, update={"task_id": self.task_id})
        else:
            graph_input = {
                "user_prompt": user_prompt,
                "iteration_count": 0,
                "task_id": self.task_id,
                "thread_id": thread_id,
                "is_stream": is_stream,
                "max_iterations": self.max_steps,
                "step_interval": self.step_interval,
                "keep_last_n_screenshots": 5,
            }

        return graph_input, config

    @traceable
    async def astream(
        self,
        user_prompt: str,
        is_stream: bool,
        thread_id: str | None = None,
    ):
        try:
            if thread_id is None:
                thread_id = str(uuid.uuid4())

            graph_input, config = self._prepare_graph_input(
                user_prompt,
                is_stream,
                thread_id,
            )

            async for chunk in self.graph.astream(
                input=graph_input,
                config=config,
                stream_mode=["messages", "custom"],
            ):
                for message_part in stream_messages(chunk, is_stream, self.task_id):
                    yield message_part

        except GraphRecursionError:
            yield format_sse(
                SSESummaryMessageData(
                    id=str(uuid.uuid4()),
                    task_id=self.task_id,
                    role="assistant",
                    type="summary",
                    content="Agent 对话次数到达限制，如您想要继续对话，请提示'继续'",
                )
            )
        except Exception as e:
            self.logger.exception(f"exit graph by error, {e}")
            raise

    @traceable
    async def run(
        self,
        user_prompt: str,
        thread_id: str | None = None,
        output_format: type[BaseModel] | None = None,
    ) -> AgentResponse:
        try:
            if thread_id is None:
                thread_id = str(uuid.uuid4())

            graph_input, config = self._prepare_graph_input(
                user_prompt=user_prompt,
                thread_id=thread_id,
                is_stream=False,
            )

            final_state = await self.graph.ainvoke(
                input=graph_input,
                config=config,
            )

            # 构建基本信息
            info = AgentInfo.create(
                final_state=final_state,
                user_prompt=user_prompt,
            )

            # 构建结果信息 - 融合结构化输出处理和状态分析
            status = "unknown"
            summary = None
            error = None
            structured_output = None

            # 分析最终状态确定任务状态
            tool_calls = final_state.get("tool_calls", [])
            if tool_calls:
                last_tool_call = tool_calls[-1]
                if last_tool_call.get("tool_name") == "finished":
                    status = "success"
                    summary = str(last_tool_call.get("tool_output", ""))
                    # 尝试生成结构化输出（仅在任务成功时）
                    if output_format:
                        messages = final_state.get("messages", [])
                        final_tool_call = last_tool_call.get("tool_call", {})
                        final_tool_output = last_tool_call.get("tool_output", "")

                        try:
                            structured_output = await summary_node(
                                llm=self.llm,
                                output_format=output_format,
                                user_prompt=user_prompt,
                                iteration_count=final_state.get("iteration_count", 0),
                                final_tool_call=final_tool_call,
                                final_tool_output=final_tool_output,
                                messages=messages,
                            )
                        except Exception as e:
                            # 结构化输出失败，记录错误但不影响任务状态
                            error = f"Structured output error: {e!s}"
                            self.logger.exception(f"Structured output generation failed: {e}")

                elif last_tool_call.get("tool_name") == "request_user":
                    status = "request_user"
                elif last_tool_call.get("tool_name") == "error_action":
                    status = "error"
                    error = str(last_tool_call.get("tool_output", ""))

            result = AgentResult(
                summary=summary,
                error=error,
                structured_output=structured_output,
                status=status,
            )

            # 构建历史记录
            history_list = []

            # 获取状态历史记录并反转，因为 get_state_history 返回倒序结果
            state_history = list(reversed(list(self.graph.get_state_history(config=config))))

            for i, state_snapshot in enumerate(state_history):
                # 计算持续时间
                duration = 0.0
                if i < len(state_history) - 1:
                    next_snapshot = state_history[i + 1]
                    if hasattr(state_snapshot, "created_at") and hasattr(next_snapshot, "created_at"):
                        try:
                            # 解析时间字符串为 datetime 对象
                            current_time = datetime.fromisoformat(state_snapshot.created_at)
                            next_time = datetime.fromisoformat(next_snapshot.created_at)
                            duration = (next_time - current_time).total_seconds()
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Failed to parse created_at timestamp: {e}")
                            duration = 0.0

                # 使用静态方法创建 AgentHistory 对象
                agent_history = AgentHistory.create(
                    state_snapshot=state_snapshot,
                    duration=duration,
                )

                history_list.append(agent_history)

            # 使用静态方法构建 AgentResponse
            return AgentResponse.create(
                info=info,
                result=result,
                history=history_list,
                final_state=final_state,
            )

        except GraphRecursionError as e:
            self.logger.exception(f"Graph recursion limit reached: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"exit graph by error, {e}")
            raise
