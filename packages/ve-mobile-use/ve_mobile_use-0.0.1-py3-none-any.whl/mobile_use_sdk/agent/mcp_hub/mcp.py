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

import asyncio
import logging
from contextlib import AsyncExitStack

from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)


class MCPHub:
    def __init__(self, mcp_json: dict | None = None) -> None:
        self.mcp_json = mcp_json or {}
        self.client: MultiServerMCPClient | None = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self._tools_cache: dict[str, list] = {}  # 添加缓存
        self.create_client()

    def _get_mcp_servers(self) -> dict:
        """获取MCP服务器配置，只支持新的mcpServers格式."""
        if not self.mcp_json or "mcpServers" not in self.mcp_json:
            return {}

        return self.mcp_json["mcpServers"]

    def update_mcp_json(self, mcp_json: dict) -> None:
        self.mcp_json.update(mcp_json)
        self.create_client()

    def add_mcp_json(self, key: str, update_key_content: dict) -> None:
        # 确保存在mcpServers结构
        if "mcpServers" not in self.mcp_json:
            self.mcp_json["mcpServers"] = {}

        if key in self.mcp_json["mcpServers"]:
            self.mcp_json["mcpServers"][key].update(update_key_content)
        else:
            self.mcp_json["mcpServers"][key] = update_key_content

        self.create_client()

    def create_client(self) -> None:
        mcp_servers = self._get_mcp_servers()
        if not mcp_servers:
            return

        # 验证每个服务器配置都包含必要的字段
        for server_name, config in mcp_servers.items():
            if "transport" not in config:
                logger.error(f"Server {server_name} missing 'transport' field: {config}")
                raise ValueError(f"Server {server_name} configuration missing 'transport' field")
            if "url" not in config:
                logger.error(f"Server {server_name} missing 'url' field: {config}")
                raise ValueError(f"Server {server_name} configuration missing 'url' field")

        self.client = MultiServerMCPClient(mcp_servers)
        self.invalidate_tools_cache()  # 配置变化时清除缓存

    async def create_all_sessions(self) -> None:
        mcp_servers = self._get_mcp_servers()
        tasks = []
        for key in mcp_servers:
            task = asyncio.create_task(self.session(key))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def session(self, key: str):
        if key in self.sessions:
            return self.sessions[key]

        self.sessions[key] = await self.exit_stack.enter_async_context(self.client.session(key))

        return self.sessions[key]

    async def aclose(self) -> None:
        try:
            await self.exit_stack.aclose()
            self.sessions = {}
            logger.debug("MCP sessions closed successfully")
        except Exception:
            self.sessions = {}

    async def call_tool(self, mcp_server_name: str, name: str, arguments: dict):
        session = await self.session(mcp_server_name)
        if not session:
            raise ValueError("MCP session is not valid")

        response = await session.call_tool(name, arguments)
        if not self.is_valid_mcp_response(response):
            text_content = response.content[0].text if response.content[0].text else "MCP工具调用失败，未返回错误信息"
            raise Exception(text_content)
        return response

    def is_valid_mcp_response(self, result) -> bool:
        if result.isError:
            return False

        if len(result.content) == 0:
            return False

        # 当前阶段只处理 text 类型的
        if result.content[0].type != "text":
            return False

        text_content = result.content[0].text
        return not (text_content == "{}" or "Error" in text_content)

    async def get_tools(self, mcp_server_name: str | None = None):
        if mcp_server_name:
            # 检查缓存
            if mcp_server_name in self._tools_cache:
                return self._tools_cache[mcp_server_name]

            tools = [(mcp_server_name, tool) for tool in await self.client.get_tools(server_name=mcp_server_name)]
            # 存入缓存
            self._tools_cache[mcp_server_name] = tools
            return tools
        # 检查全局缓存
        cache_key = "_all_tools"
        if cache_key in self._tools_cache:
            return self._tools_cache[cache_key]

        tools = []
        mcp_servers = self._get_mcp_servers()
        for key in mcp_servers:
            tools.extend(await self.get_tools(key))

        # 存入缓存
        self._tools_cache[cache_key] = tools
        return tools

    def invalidate_tools_cache(self) -> None:
        """当MCP配置发生变化时清除缓存."""
        self._tools_cache.clear()
