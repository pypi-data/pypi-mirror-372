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
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConnectionFactory(ABC, Generic[T]):
    """连接工厂抽象类."""

    @abstractmethod
    async def create_connection(self, config: dict) -> T:
        """创建连接."""
        pass

    @abstractmethod
    async def close_connection(self, connection: T) -> None:
        """关闭连接."""
        pass

    @abstractmethod
    async def test_connection(self, connection: T) -> bool:
        """测试连接是否可用."""
        pass

    @abstractmethod
    def get_config_key(self, config: dict) -> str:
        """根据配置生成唯一键."""
        pass


class ConnectionPoolManager(Generic[T]):
    """通用连接池管理器."""

    def __init__(self, factory: ConnectionFactory[T], connection_timeout: int = 600) -> None:
        self.factory = factory
        self.connection_timeout = connection_timeout  # 连接超时时间（秒）
        self.max_retries = 3

        # 连接存储
        self._connections: dict[str, T] = {}
        self._connection_metadata: dict[str, dict] = {}

        # 并发控制
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def get_or_create_connection(self, config: dict) -> T:
        """获取或创建连接 - 处理并发竞争."""
        config_key = self.factory.get_config_key(config)

        # 获取或创建该配置的锁
        async with self._global_lock:
            if config_key not in self._locks:
                self._locks[config_key] = asyncio.Lock()
            connection_lock = self._locks[config_key]

        # 使用配置特定的锁防止并发创建
        async with connection_lock:
            # 双重检查模式
            if config_key in self._connections:
                connection = self._connections[config_key]
                metadata = self._connection_metadata[config_key]

                # 检查连接是否过期
                if self._is_connection_expired(metadata):
                    logger.info(f"连接 {config_key} 已过期，重新创建")
                    await self._recreate_connection(config_key, config)
                    return self._connections[config_key]

                # 测试连接是否可用
                # if not await self.factory.test_connection(connection):
                #     logger.warning(f"连接 {config_key} 不可用，重新创建")
                #     await self._recreate_connection(config_key, config)
                #     return self._connections[config_key]

                logger.debug(f"复用现有连接: {config_key}")
                return connection
            # 创建新连接
            return await self._create_new_connection(config_key, config)

    async def _create_new_connection(self, config_key: str, config: dict) -> T:
        """创建新连接."""
        for retry in range(self.max_retries):
            try:
                logger.info(f"创建新连接: {config_key} (尝试 {retry + 1}/{self.max_retries})")

                connection = await self.factory.create_connection(config)

                self._connections[config_key] = connection
                self._connection_metadata[config_key] = {
                    "created_at": time.time(),
                    "config": config,
                    "retry_count": retry,
                    "usage_count": 0,
                }

                logger.info(f"✅ 成功创建连接: {config_key}")
                return connection

            except Exception as e:
                logger.exception(f"❌ 创建连接失败 {config_key} (尝试 {retry + 1}/{self.max_retries}): {e}")
                if retry == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**retry)  # 指数退避
        return None

    async def _recreate_connection(self, config_key: str, config: dict) -> None:
        """重新创建连接."""
        # 清理旧连接
        if config_key in self._connections:
            try:
                await self.factory.close_connection(self._connections[config_key])
            except Exception as e:
                logger.exception(f"关闭旧连接失败: {e}")
            finally:
                self._connections.pop(config_key, None)
                self._connection_metadata.pop(config_key, None)

        # 创建新连接
        await self._create_new_connection(config_key, config)

    def _is_connection_expired(self, metadata: dict) -> bool:
        """检查连接是否过期."""
        created_at = metadata.get("created_at", 0)
        return time.time() - created_at > self.connection_timeout

    async def increment_usage(self, config: dict) -> None:
        """增加使用计数."""
        config_key = self.factory.get_config_key(config)
        if config_key in self._connection_metadata:
            self._connection_metadata[config_key]["usage_count"] += 1

    async def cleanup_expired_expired_connections(self) -> None:
        """清理过期连接."""
        async with self._global_lock:
            expired_keys = []
            for key, metadata in self._connection_metadata.items():
                if self._is_connection_expired(metadata):
                    expired_keys.append(key)

            for key in expired_keys:
                if key in self._locks:
                    async with self._locks[key]:
                        try:
                            await self.factory.close_connection(self._connections[key])
                        except Exception as e:
                            logger.exception(f"清理过期连接 {key} 失败: {e}")
                        finally:
                            self._connections.pop(key, None)
                            self._connection_metadata.pop(key, None)
                            self._locks.pop(key, None)
                            logger.info(f"🗑️ 已清理过期连接: {key}")

    async def cleanup_all_connections(self) -> None:
        """清理所有连接."""
        async with self._global_lock:
            for key in self._connections:
                await self.factory.close_connection(self._connections[key])
            self._connections.clear()
            self._connection_metadata.clear()

    def get_connection_stats(self) -> dict:
        """获取连接池统计信息."""
        return {
            "total_connections": len(self._connections),
            "connections": {
                key: {
                    "created_at": metadata["created_at"],
                    "usage_count": metadata["usage_count"],
                    "age_seconds": time.time() - metadata["created_at"],
                }
                for key, metadata in self._connection_metadata.items()
            },
        }
