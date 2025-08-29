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

from typing import Any, Optional

from pydantic import BaseModel

from mobile_use_sdk.agent.graph.state import MobileUseAgentState


class AgentParams(BaseModel):
    """Agent执行参数

    包含Agent运行时所需的基本参数配置
    """

    thread_id: str  # 线程ID，用于标识会话
    task_id: str  # 任务ID，用于标识具体任务
    max_iterations: int  # 最大迭代次数，防止无限循环


# Agent响应相关的数据模型定义
class AgentInfo(BaseModel):
    """Agent基本信息

    包含Agent执行过程中的基础配置和用户输入信息
    """

    params: AgentParams  # Agent执行参数，包含线程ID、任务ID等
    user_prompt: str  # 用户输入的提示词或指令

    @staticmethod
    def create(
        final_state: dict[str, Any],
        user_prompt: str = "",
    ) -> "AgentInfo":
        """从最终状态创建 AgentInfo 对象

        Args:
            final_state: 图执行后的最终状态
            user_prompt: 用户输入的提示词

        Returns:
            AgentInfo: 构建的信息对象
        """
        return AgentInfo(
            params=AgentParams(
                thread_id=str(final_state.get("thread_id")),
                task_id=final_state.get("task_id"),
                max_iterations=final_state.get("max_iterations"),
            ),
            user_prompt=final_state.get("user_prompt", user_prompt),
        )


class AgentResult(BaseModel):
    """Agent执行结果

    包含Agent执行完成后的输出结果，包括文本摘要和结构化数据
    """

    summary: Optional[str] = None  # 执行结果的文本摘要描述
    error: Optional[str] = None  # 执行过程中的错误信息，None表示无错误
    structured_output: Optional[dict[str, Any]] = None  # 结构化输出数据，用于程序化处理
    status: Optional[str] = None


class StepMetadata(BaseModel):
    """Agent执行步骤的元数据

    记录每个步骤的执行时间等元信息
    """

    duration_seconds: float = 0.0  # 步骤执行耗时（秒）
    checkpoint_id: Optional[str] = None  # 检查点ID


class AgentTask(BaseModel):
    task_id: str  # 任务ID
    task_name: str  # 任务名称
    update: dict[str, Any] = {}  # 任务更新


class AgentHistory(BaseModel):
    """Agent执行历史记录项

    记录Agent执行过程中每个步骤的详细信息，包括输出、结果、状态等
    """

    state: MobileUseAgentState = None  # 执行时的界面状态
    metadata: StepMetadata = None  # 步骤的元数据信息
    tasks: list[AgentTask] = []

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """自定义序列化方法

        处理循环引用问题，安全地将对象转换为字典格式

        Returns:
            dict: 序列化后的字典数据
        """
        return {
            "state": self.state.model_dump(**kwargs),
            "metadata": self.metadata.model_dump(**kwargs) if self.metadata else None,
        }

    @staticmethod
    def create(
        state_snapshot,
        duration: float = 0.0,
    ) -> "AgentHistory":
        """从状态快照创建 AgentHistory 对象

        Args:
            state_snapshot: 当前状态快照
            duration: 已计算的持续时间（秒）
            logger: 日志记录器

        Returns:
            AgentHistory: 构建的历史记录对象
        """
        agent_history = AgentHistory()

        # 设置 metadata
        if hasattr(state_snapshot, "created_at"):
            # 获取 checkpoint_id
            checkpoint_id = state_snapshot.config.get("configurable", {}).get("checkpoint_id")

            agent_history.metadata = StepMetadata(duration_seconds=duration, checkpoint_id=checkpoint_id)

        # 设置 state（screenshot 等）
        if hasattr(state_snapshot, "values") and state_snapshot.values:
            agent_history.state = state_snapshot.values

        if hasattr(state_snapshot, "tasks") and state_snapshot.tasks:
            agent_history.tasks = [
                AgentTask(task_id=task.id, task_name=task.name, update=task.result or {})
                for task in state_snapshot.tasks
            ]

        return agent_history


class AgentResponse(BaseModel):
    """Agent执行响应的完整结果

    包含Agent执行过程的完整信息，包括基本信息、最终结果、执行历史和资源使用情况。
    这是用户调用Agent时获得的主要返回对象。
    """

    info: AgentInfo  # Agent的基本信息，包含执行参数和用户输入
    result: AgentResult  # 最终执行结果，包含摘要和结构化输出
    history: list[AgentHistory]  # 完整的执行历史记录列表
    final_state: dict[str, Any]  # 图执行后的最终状态

    def total_duration_seconds(self) -> float:
        """获取所有执行步骤的总耗时

        计算Agent执行过程中所有步骤的累计时间

        Returns:
                float: 总执行时间（秒）
        """
        total = 0.0
        for h in self.history:
            if h.metadata:
                total += h.metadata.duration_seconds
        return total

    def final_state(self) -> None | dict:
        return self.final_state

    def errors(self) -> str | None:
        """获取所有执行步骤的错误信息

        返回每个步骤的错误信息，无错误的步骤返回None

        Returns:
                list[str | None]: 错误信息列表，每个元素对应一个步骤
        """
        return self.result.error

    def is_done(self) -> bool:
        """检查Agent是否已完成执行

        判断Agent是否已经完成所有任务

        Returns:
                bool: True表示已完成，False表示未完成
        """
        return self.result.status == "success"

    def tool_calls(self) -> list[dict[str, Any]]:
        """获取所有工具调用

        从 final_state 中获取工具调用列表

        Returns:
                list[Dict[str, Any]]: 工具调用列表
        """
        return self.final_state.get("tool_calls", [])

    def screenshots(self, n_last: int | None = None) -> list[Any]:
        """获取执行历史中的截图数据

        从 final_state 中获取已组装好的截图信息

        Args:
                n_last: 获取最后n个截图，None表示获取所有
                return_none_if_not_screenshot: 没有截图时是否返回None

        Returns:
                list[str | None]: 截图数据列表
        """
        # 从 final_state 中直接获取已组装好的截图
        screenshots = self.final_state.get("screenshots", {})

        screenshots = list(screenshots.values()) if isinstance(screenshots, dict) else screenshots

        # 如果指定了 n_last，只返回最后 n 个
        if n_last is not None and len(screenshots) > n_last:
            screenshots = screenshots[-n_last:]

        return screenshots

    def messages(self) -> list[Any]:
        """获取所有消息

        从 final_state 中获取所有消息
        """
        return self.final_state.get("messages", [])

    @staticmethod
    def create(
        info: AgentInfo,
        result: AgentResult,
        history: Optional[list[AgentHistory]] = None,
        final_state: Optional[dict[str, Any]] = None,
    ) -> "AgentResponse":
        """创建 AgentResponse 对象

        Args:
                info: Agent基本信息
                result: Agent执行结果
                history: 历史记录列表
                final_state: 图执行后的最终状态

        Returns:
                AgentResponse: 构建完成的响应对象
        """
        return AgentResponse(
            info=info,
            result=result,
            history=history or [],
            final_state=final_state or {},
        )
