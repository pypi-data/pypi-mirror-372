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

import ast
import logging
import re
from typing import Any

from mobile_use_sdk.agent.infra.model import ToolCall

logger = logging.getLogger(__name__)


class ActionParser:
    """通用的工具调用字符串解析器."""

    @staticmethod
    def parse_tool_call_string(tool_call_str: str) -> ToolCall | None:
        """将工具调用字符串转换为 ToolCall JSON 格式.

        Args:
            tool_call_str: 工具调用字符串，例如 "wait(t='5')" 或 "tap(x=100, y=200)"

        Returns:
            ToolCall 格式的字典，例如 {"name": "wait", "arguments": {"t": "5"}}
            如果解析失败则返回 None
        """
        if not tool_call_str or not isinstance(tool_call_str, str):
            logger.error(f"工具调用字符串为空或类型错误: {tool_call_str!r}")
            return None

        # 去除首尾空格
        tool_call_str = tool_call_str.strip()
        # finished(content='已为你关闭抖音应用，任务完成。')\n```
        tool_call_str = tool_call_str.strip("\n```")

        try:
            # 使用正则表达式匹配函数名和参数，支持跨行内容
            pattern = r"^([\w:]+)\s*\((.*)\)\s*$"
            match = re.match(pattern, tool_call_str, re.DOTALL)

            if not match:
                logger.error(f"无法解析工具调用字符串: {tool_call_str[:200]!r}... (长度: {len(tool_call_str)})")
                return None

            function_name = match.group(1)
            params_str = match.group(2).strip()

            # 解析参数
            arguments = ActionParser._parse_arguments(params_str)

            return {"name": function_name, "arguments": arguments}

        except Exception as e:
            logger.exception(f"解析工具调用字符串时发生异常: {tool_call_str!r}, 错误: {e}")
            return None

    @staticmethod
    def _parse_arguments(params_str: str) -> dict[str, Any]:
        """解析参数字符串为字典.

        支持多种格式：
        - "t='5'" -> {"t": "5"}
        - "x=100, y=200" -> {"x": 100, "y": 200}
        - "text='hello world', count=3" -> {"text": "hello world", "count": 3}
        - "" -> {}
        """
        if not params_str:
            return {}

        try:
            # 方法1: 尝试使用 AST 安全解析（最安全的方式）
            return ActionParser._parse_with_ast(params_str)
        except Exception as ast_error:
            try:
                # 方法2: 使用正则表达式手动解析
                return ActionParser._parse_with_regex(params_str)
            except Exception as regex_error:
                logger.exception(f"解析参数失败: {params_str!r}, AST错误: {ast_error}, 正则错误: {regex_error}")
                return {}

    @staticmethod
    def _parse_with_ast(params_str: str) -> dict[str, Any]:
        """使用 AST 安全解析参数（推荐方法）."""
        # 构造一个伪函数调用，让 AST 解析
        fake_call = f"func({params_str})"

        try:
            tree = ast.parse(fake_call, mode="eval")
            call_node = tree.body

            if not isinstance(call_node, ast.Call):
                raise ValueError("不是有效的函数调用")

            result = {}

            # 解析关键字参数
            for keyword in call_node.keywords:
                if keyword.arg:
                    value = ActionParser._ast_node_to_value(keyword.value)
                    result[keyword.arg] = value

            # 解析位置参数（如果有的话，按照约定转换为关键字参数）
            for i, arg in enumerate(call_node.args):
                key = f"arg_{i}"  # 位置参数使用 arg_0, arg_1... 作为键
                value = ActionParser._ast_node_to_value(arg)
                result[key] = value

            return result

        except Exception as e:
            raise ValueError(f"AST 解析失败: {e}")

    @staticmethod
    def _ast_node_to_value(node: ast.AST) -> Any:
        """将 AST 节点转换为 Python 值（现代化实现）."""
        # 优先使用现代的 ast.Constant（Python 3.8+）
        if isinstance(node, ast.Constant):
            return node.value

        # 处理复合类型
        if isinstance(node, ast.List):
            return [ActionParser._ast_node_to_value(item) for item in node.elts]
        if isinstance(node, ast.Dict):
            return {
                ActionParser._ast_node_to_value(k): ActionParser._ast_node_to_value(v)
                for k, v in zip(node.keys, node.values, strict=False)
            }
        if isinstance(node, ast.Name):
            # 处理变量名，将其转换为字符串
            return node.id

        # 向后兼容：处理旧版本的字面量类型（仅在必要时）
        if hasattr(ast, "Str") and isinstance(node, ast.Str):
            # Python < 3.8 兼容性
            return node.s
        if hasattr(ast, "Num") and isinstance(node, ast.Num):
            # Python < 3.8 兼容性
            return node.n
        if hasattr(ast, "NameConstant") and isinstance(node, ast.NameConstant):
            # Python < 3.8 兼容性
            return node.value

        # 对于复杂表达式，优先尝试现代方法
        try:
            return ast.literal_eval(node)
        except Exception:
            # 尝试使用 ast.unparse（Python 3.9+）
            try:
                if hasattr(ast, "unparse"):
                    return ast.unparse(node)
                # 降级到字符串表示
                raise ValueError("需要正则表达式处理")
            except Exception:
                # 抛出异常让正则表达式处理
                raise ValueError(f"复杂表达式无法转换: {type(node).__name__}")

    @staticmethod
    def _parse_with_regex(params_str: str) -> dict[str, Any]:
        """使用正则表达式手动解析参数（备用方法）."""
        result = {}

        # 增强的正则解析，支持复杂的参数值
        # 首先尝试匹配基本的参数结构，然后对复杂内容进行特殊处理

        # 方法1：尝试智能分割参数
        try:
            params = ActionParser._split_params_smart(params_str)

            for param in params:
                param = param.strip()
                if not param:
                    continue

                # 匹配 key=value 模式，使用DOTALL支持跨行
                eq_match = re.match(r"^(\w+)\s*=\s*(.+)$", param, re.DOTALL)
                if eq_match:
                    key = eq_match.group(1)
                    value_str = eq_match.group(2).strip()

                    # 处理值：去除外层引号，但保留内部的复杂结构
                    if (value_str.startswith("'") and value_str.endswith("'")) or (
                        value_str.startswith('"') and value_str.endswith('"')
                    ):
                        value = value_str[1:-1]
                    else:
                        value = value_str

                    result[key] = value

            if result:
                return result
        except Exception as e:
            logger.debug(f"智能分割方法失败: {e}")

        # 方法2：如果智能分割失败，使用更强力的正则匹配
        return ActionParser._parse_with_enhanced_regex(params_str)

    @staticmethod
    def _parse_with_enhanced_regex(params_str: str) -> dict[str, Any]:
        """增强的正则解析，专门处理复杂参数."""
        result = {}

        # 使用正则表达式匹配 key=value 模式，支持复杂的值
        # 这个模式可以匹配：content='复杂的字符串内容...'
        pattern = r"(\w+)\s*=\s*(['\"])(.*?)\2(?:\s*,\s*|$)"

        matches = re.finditer(pattern, params_str, re.DOTALL)
        for match in matches:
            key = match.group(1)
            value = match.group(3)
            result[key] = value

        # 如果还没匹配到，尝试更宽松的模式
        if not result:
            # 匹配没有引号的值
            pattern2 = r"(\w+)\s*=\s*([^,]+)(?:\s*,\s*|$)"
            matches2 = re.finditer(pattern2, params_str)
            for match in matches2:
                key = match.group(1)
                value = match.group(2).strip()
                result[key] = value

        return result

    @staticmethod
    def _split_params_smart(params_str: str) -> list:
        """智能分割参数字符串，处理引号内的逗号和括号嵌套."""
        if not params_str:
            return []

        params = []
        current_param = ""
        in_quote = False
        quote_char = None
        paren_depth = 0  # 括号嵌套深度
        bracket_depth = 0  # 方括号嵌套深度

        i = 0
        while i < len(params_str):
            char = params_str[i]

            if char in ("'", '"') and not in_quote:
                # 开始引号
                in_quote = True
                quote_char = char
                current_param += char
            elif char == quote_char and in_quote:
                # 结束引号（检查是否转义）
                # 计算前面有多少个连续的反斜杠
                backslash_count = 0
                j = i - 1
                while j >= 0 and params_str[j] == "\\":
                    backslash_count += 1
                    j -= 1

                # 如果反斜杠数量是偶数（包括0），则引号没有被转义
                if backslash_count % 2 == 0:
                    in_quote = False
                    quote_char = None
                current_param += char
            elif not in_quote:
                # 在引号外处理括号嵌套
                if char == "(":
                    paren_depth += 1
                    current_param += char
                elif char == ")":
                    paren_depth -= 1
                    current_param += char
                elif char == "[":
                    bracket_depth += 1
                    current_param += char
                elif char == "]":
                    bracket_depth -= 1
                    current_param += char
                elif char == "," and paren_depth == 0 and bracket_depth == 0:
                    # 参数分隔符（不在引号内且不在括号内）
                    if current_param.strip():
                        params.append(current_param.strip())
                    current_param = ""
                else:
                    current_param += char
            else:
                current_param += char

            i += 1

        # 添加最后一个参数
        if current_param.strip():
            params.append(current_param.strip())

        return params
