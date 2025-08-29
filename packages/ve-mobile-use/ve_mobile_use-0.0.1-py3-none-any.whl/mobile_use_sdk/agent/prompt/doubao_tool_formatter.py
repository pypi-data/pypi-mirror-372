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

from mobile_use_sdk.agent.tools.tool.abc import Tool


class DoubaoPromptFormatter:
    """统一的提示格式化器，按照 doubao_system_prompt 的格式输出工具."""

    @staticmethod
    def format_tool_to_action_space(tool: Tool) -> str:
        """将工具格式化为 Action Space 风格的字符串."""
        params = []
        # 解析参数并生成函数调用格式
        if hasattr(tool, "parameters") and tool.parameters and "properties" in tool.parameters:
            for param_name, param_info in tool.parameters.get("properties").items():
                if isinstance(param_info, dict):
                    param_type = param_info.get("type", "string")
                    if param_type == "string":
                        params.append(f"{param_name}=''")
                    elif param_type == "number":
                        params.append(f"{param_name}='x'")
                    else:
                        params.append(f"{param_name}=''")
        # 生成函数调用格式
        param_str = ", ".join(params) if params else ""
        function_call = f"{tool.name}({param_str})"
        # 添加注释描述
        if tool.description:
            return f"{function_call} # {tool.description}"
        return function_call

    @staticmethod
    def format_tools_to_action_space(tools: list[Tool]) -> str:
        """将工具列表格式化为完整的 Action Space."""
        formatted_tools = [DoubaoPromptFormatter.format_tool_to_action_space(tool) for tool in tools]
        return "\n".join(formatted_tools)
