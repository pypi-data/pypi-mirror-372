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

import json
from collections.abc import Callable
from typing import Any


def parse_chunk(chunk):
    """美化输出处理函数"""
    try:
        # 如果 chunk 是字符串，尝试解析为 JSON
        if isinstance(chunk, str):
            # 处理 SSE 格式的数据
            if chunk.startswith("data: "):
                json_str = chunk[6:]  # 去掉 'data: ' 前缀
                if json_str.strip() == "[DONE]":
                    return None
                chunk = json.loads(json_str)
            else:
                chunk = json.loads(chunk)

        return chunk
    except (json.JSONDecodeError, AttributeError):
        # 如果不是有效的 JSON，直接返回原始数据
        return chunk


class StdioStreamOutput:
    def __init__(self):
        self.tasks = {}  # 存储不同 task_id 的消息
        self.user_input_callback: Callable[[str], None] | None = None
        self.default_input: str | None = None

    def set_user_input_callback(self, callback: Callable[[str], None], default_input: str | None):
        """设置用户输入回调函数"""
        self.user_input_callback = callback
        if default_input:
            self.default_input = default_input

    def register_task(self, chunk) -> str:
        parsed_chunk = parse_chunk(chunk)
        if parsed_chunk is None:
            return
        if isinstance(parsed_chunk, dict):
            self.handle_message(parsed_chunk)
        else:
            print(f"📨 原始消息: {parsed_chunk}")

    def handle_message(self, chunk: dict[str, Any]):
        """处理单个 SSE 消息"""
        if "task_id" not in chunk:
            return None

        task_id = chunk["task_id"]

        # 初始化任务数据
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                "reasoning_steps": {},
                "think_steps": {},
                "tools": {},
                "summary": "",
                "user_interrupts": [],
            }

        task_data = self.tasks[task_id]

        # 根据消息类型处理
        msg_type = chunk.get("type")

        if msg_type == "reasoning":
            self._handle_reasoning(task_data, chunk)
        elif msg_type == "think":
            self._handle_think(task_data, chunk)
        elif msg_type == "tool":
            self._handle_tool(task_data, chunk)
        elif msg_type == "summary":
            self._handle_summary(task_data, chunk)
        elif msg_type == "user_interrupt":
            return self._handle_user_interrupt(task_data, chunk)
        return None

    def _handle_reasoning(self, task_data: dict, chunk: dict):
        """处理 reasoning 类型消息"""
        step_id = chunk["id"]
        content = chunk.get("content", "")

        if step_id not in task_data["reasoning_steps"]:
            task_data["reasoning_steps"][step_id] = ""
            print("\n🤔 推理: ", end="", flush=True)

        task_data["reasoning_steps"][step_id] += content
        print(content, end="", flush=True)

    def _handle_think(self, task_data: dict, chunk: dict):
        """处理 think 类型消息"""
        step_id = chunk["id"]
        content = chunk.get("content", "")

        if step_id not in task_data["think_steps"]:
            task_data["think_steps"][step_id] = ""
            print("\n💭 思考: ", end="", flush=True)

        task_data["think_steps"][step_id] += content
        print(content, end="", flush=True)

    def _handle_tool(self, task_data: dict, chunk: dict):
        """处理 tool 类型消息"""
        tool_id = chunk.get("tool_id")
        tool_name = chunk.get("tool_name", "")
        status = chunk.get("status", "")
        tool_type = chunk.get("tool_type", "")

        if tool_id not in task_data["tools"]:
            task_data["tools"][tool_id] = {
                "name": tool_name,
                "input": None,
                "output": None,
                "status": status,
            }

        tool_data = task_data["tools"][tool_id]
        tool_data["status"] = status

        if tool_type == "tool_input":
            tool_data["input"] = chunk.get("tool_input")
            print(f"\n🔧 工具调用: {tool_name}")
            if tool_data["input"]:
                print(f"   输入: {json.dumps(tool_data['input'], ensure_ascii=False, indent=2)}")

        elif tool_type == "tool_output":
            tool_data["output"] = chunk.get("tool_output")
            if tool_data["output"]:
                print(f"   输出: {tool_data['output']}")

        # 显示工具状态
        if status == "start":
            print("   状态: 开始执行")
        elif status == "success":
            print("   状态: ✅ 执行成功")
        elif status == "stop":
            print("   状态: ⏹️ 停止执行")

    def _handle_summary(self, task_data: dict, chunk: dict):
        """处理 summary 类型消息"""
        content = chunk.get("content", "")

        if not task_data["summary"]:
            print("\n📝 总结: ", end="", flush=True)

        task_data["summary"] += content
        print(content, end="", flush=True)

    def _handle_user_interrupt(self, task_data: dict, chunk: dict):
        """处理 user_interrupt 类型消息"""
        interrupt_type = chunk.get("interrupt_type", "text")
        content = chunk.get("content", "")

        print(f"\n⚠️ 需要用户输入: {content}")

        if interrupt_type == "text":
            user_input = input("请输入: ") if not self.default_input else self.default_input
            task_data["user_interrupts"].append({"prompt": content, "response": user_input})

            # 如果设置了回调函数，调用它来处理用户输入
            if self.user_input_callback:
                self.user_input_callback(user_input)

            return user_input

        return None
