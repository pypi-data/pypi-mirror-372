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

from langchain_core.tools import StructuredTool

from mobile_use_sdk.agent.mcp_hub.mcp import MCPHub
from mobile_use_sdk.agent.tools.tool.abc import Tool


class McpTool(Tool):
    def __init__(self, mcp_hub: MCPHub, mcp_name: str, mcp_tool: StructuredTool) -> None:
        super().__init__(
            name=f"{mcp_name}:{mcp_tool.name}",
            description=mcp_tool.description,
            parameters=mcp_tool.args_schema,
        )
        self.mcp_name = mcp_name
        self.mcp_tool = mcp_tool
        self.mcp_hub = mcp_hub

    async def handler(self, args: dict | None = None) -> str | None:
        if args is None:
            args = {}
        toolResults = await self.mcp_hub.call_tool(self.mcp_name, self.mcp_tool.name, args)
        contents = [content.text if content.type == "text" else None for content in toolResults.content]
        # 暂时只取第一个
        return contents[0]
