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

from mobile_use_sdk.agent.infra.model import ToolCall
from mobile_use_sdk.agent.mcp_hub.mcp import MCPHub
from mobile_use_sdk.agent.prompt.doubao_tool_formatter import DoubaoPromptFormatter
from mobile_use_sdk.agent.tools.tool import (
    ErrorTool,
    FinishedTool,
    RequestUserTool,
    WaitTool,
)
from mobile_use_sdk.agent.tools.tool.abc import SpecialTool, Tool
from mobile_use_sdk.agent.tools.tool.mcp_tool import McpTool
from mobile_use_sdk.mobile.abc import Mobile


class Tools:
    def __init__(
        self,
        tools: list[Tool | SpecialTool | McpTool],
        mcp_tools: list[McpTool],
        mobile: Mobile | None = None,
    ) -> None:
        self.tools = tools
        self.mcp_tools = mcp_tools
        self.mobile = mobile

    @classmethod
    async def from_mcp(cls, mcp_hub: MCPHub | None = None, mobile: Mobile | None = None):
        tools = [
            FinishedTool(),
            WaitTool(),
            RequestUserTool(),
            ErrorTool(),
        ]
        mcp_tools = await mcp_hub.get_tools() if mcp_hub else []
        mcp_tools = [McpTool(mcp_hub, mcp_server_name, tool) for mcp_server_name, tool in mcp_tools]

        return cls(tools, mcp_tools, mobile)

    def list_inner_tools_prompt_string(self):
        # 过滤掉 ErrorTool，在 prompt 中不显示
        filtered_tools = [tool for tool in self.tools if not isinstance(tool, ErrorTool)]
        return DoubaoPromptFormatter.format_tools_to_action_space(filtered_tools)

    def list_mcp_tools_prompt_string(self):
        return DoubaoPromptFormatter.format_tools_to_action_space(self.mcp_tools)

    def list_mobile_tools_prompt_string(self):
        """直接返回mobile自己的工具提示."""
        if self.mobile:
            return self.mobile.get_mobile_tools_prompt()
        return ""

    async def exec(self, tool_call: ToolCall):
        tool_name = tool_call["name"]
        tool_args = tool_call.get("arguments", {})

        # 首先检查是否是mobile工具
        if self.mobile and self.mobile.is_mobile_tool(tool_name):
            return await self._exec_mobile_tool(tool_name, tool_args)

        # 然后检查常规工具
        tool = self.get_tool_by_name(tool_name)
        if tool:
            return await tool.call(tool_args)
        raise ValueError(f"Tool with name {tool_name} not found")

    async def _exec_mobile_tool(self, tool_name: str, tool_args: dict):
        """执行mobile工具."""
        try:
            # 根据工具名称找到对应的方法并调用
            # 检查mobile客户端是否有对应的方法
            for method_name in dir(self.mobile):
                method = getattr(self.mobile, method_name)
                if hasattr(method, "_mobile_tool_info"):
                    tool_info = method._mobile_tool_info
                    if tool_info["name"] == tool_name:
                        result = await method(**tool_args)
                        return result if result is not None else f"{tool_name} 操作完成"

            raise ValueError(f"Mobile tool {tool_name} not found")

        except Exception as e:
            return f"{tool_name} 操作失败: {e!s}"

    def is_special_tool(self, tool_name: str):
        tool = self.get_tool_by_name(tool_name)
        return tool and tool.is_special_tool

    def get_special_message(self, tool_name: str, content: str, args: dict):
        tool = self.get_tool_by_name(tool_name)
        if tool and tool.is_special_tool:
            return tool.special_message(content, args)
        return None

    def get_special_memory(self, tool_name: str, content: str | None = None):
        tool = self.get_tool_by_name(tool_name)
        if tool and tool.is_special_tool:
            return tool.special_memory(content)
        return None

    def get_tool_by_name(self, tool_name: str) -> Tool | SpecialTool | McpTool | None:
        return next(
            (tool for tool in self.tools if tool.name == tool_name),
            next((tool for tool in self.mcp_tools if tool.name == tool_name), None),
        )

    def is_omit_sse_output(self, tool_name: str) -> bool:
        """判断是否需要省略 SSE 输出."""
        tool = self.get_tool_by_name(tool_name)
        if tool is None:
            return False
        return isinstance(tool, RequestUserTool | ErrorTool)
