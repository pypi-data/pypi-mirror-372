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


# 创建自定义Logger类
class AgentLogger:
    def __init__(self, logger_name) -> None:
        self.logger = logging.getLogger(logger_name)
        self.thread_id = None
        self.pod_id = None

    def set_context(
        self,
        thread_id: str | None = None,
        pod_id: str | None = None,
    ) -> None:
        """设置日志上下文."""
        if thread_id:
            self.thread_id = thread_id
        if pod_id:
            self.pod_id = pod_id

    def _format_message(self, msg):
        """添加上下文信息到日志消息."""
        context = []
        if self.thread_id:
            context.append(f"thread_id={self.thread_id}")
        if self.pod_id:
            context.append(f"pod_id={self.pod_id}")

        if context:
            return f"[{' '.join(context)}] {msg}"
        return msg

    def debug(self, msg, *args, **kwargs) -> None:
        self.logger.debug(self._format_message(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self.logger.info(self._format_message(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self.logger.warning(self._format_message(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self.logger.error(self._format_message(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs) -> None:
        self.logger.critical(self._format_message(msg), *args, **kwargs)
