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

import hashlib
import logging

from mobile_use_sdk.agent.mcp_hub.connection_pool_manager import ConnectionFactory
from mobile_use_sdk.agent.mcp_hub.mcp import MCPHub

logger = logging.getLogger(__name__)


class MCPConnectionFactory(ConnectionFactory[MCPHub]):
    """MCP连接工厂."""

    async def create_connection(self, config: dict) -> MCPHub:
        """创建MCP连接."""
        logger.info(f"创建MCP连接，配置: {config}")
        hub = MCPHub(config)
        await hub.create_all_sessions()
        logger.info("MCP连接创建成功")
        return hub

    async def close_connection(self, connection: MCPHub) -> None:
        """关闭MCP连接."""
        try:
            await connection.aclose()
            logger.info("MCP连接已关闭")
        except Exception as e:
            logger.exception(f"关闭MCP连接失败: {e}")

    async def test_connection(self, connection: MCPHub) -> bool:
        """测试MCP连接是否可用."""
        try:
            # 尝试获取工具列表测试连接
            await connection.get_tools()
            return True
        except Exception as e:
            logger.warning(f"MCP连接测试失败: {e}")
            return False

    def get_config_key(self, config: dict) -> str:
        """根据MCP配置生成唯一键."""
        if not config:
            return "default_mcp"

        # 标准化配置
        normalized_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                # 排序字典确保一致性
                normalized_config[key] = dict(sorted(value.items()))
            else:
                normalized_config[key] = value

        config_str = str(sorted(normalized_config.items()))
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        return f"mcp_{config_hash}"
