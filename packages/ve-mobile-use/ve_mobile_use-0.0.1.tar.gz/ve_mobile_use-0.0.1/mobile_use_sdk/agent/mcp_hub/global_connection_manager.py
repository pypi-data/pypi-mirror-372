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

from mobile_use_sdk.agent.mcp_hub.connection_pool_manager import ConnectionPoolManager
from mobile_use_sdk.agent.mcp_hub.mcp import MCPHub
from mobile_use_sdk.agent.mcp_hub.mcp_connection_factory import MCPConnectionFactory

logger = logging.getLogger(__name__)

# 创建MCP连接池管理器
mcp_connection_manager = ConnectionPoolManager[MCPHub](
    factory=MCPConnectionFactory(),
    connection_timeout=600,  # 10分钟
)


class GlobalMCPConnectionManager:
    """全局MCP连接管理器."""

    @staticmethod
    async def get_mcp_hub(mcp_config: dict | None = None) -> MCPHub:
        """获取MCP连接."""
        config = mcp_config or {}
        logger.debug(f"获取MCP连接，配置: {config}")

        hub = await mcp_connection_manager.get_or_create_connection(config)
        await mcp_connection_manager.increment_usage(config)

        logger.debug("MCP连接获取成功")
        return hub

    @staticmethod
    async def cleanup_all_expired_connections() -> None:
        """清理所有过期连接."""
        logger.info("开始清理过期连接...")

        try:
            await mcp_connection_manager.cleanup_expired_expired_connections()
            logger.info("✅ 过期连接清理完成")
        except Exception as e:
            logger.exception(f"❌ 清理过期连接失败: {e}")

    @staticmethod
    async def cleanup_all_connections() -> None:
        """清理所有连接."""
        logger.info("开始清理所有连接...")

        try:
            await mcp_connection_manager.cleanup_all_connections()
            logger.info("✅ 所有连接清理完成")
        except Exception as e:
            logger.exception(f"❌ 清理所有连接失败: {e}")

    @staticmethod
    def get_connection_stats():
        """获取所有连接池统计."""
        try:
            mcp_stats = mcp_connection_manager.get_connection_stats()

            return {
                "mcp_connections": mcp_stats,
                "summary": {
                    "total_mcp_connections": mcp_stats["total_connections"],
                    "total_connections": mcp_stats["total_connections"],
                },
            }
        except Exception as e:
            logger.exception(f"获取连接统计失败: {e}")
            return {
                "error": str(e),
                "mcp_connections": {"total_connections": 0, "connections": {}},
                "summary": {"total_mcp_connections": 0, "total_connections": 0},
            }


# 全局MCP连接管理器实例
mcp_manager = GlobalMCPConnectionManager()
