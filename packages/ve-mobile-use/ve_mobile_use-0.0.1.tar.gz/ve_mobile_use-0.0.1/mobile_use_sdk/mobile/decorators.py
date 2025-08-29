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

import inspect
import re
from functools import wraps
from typing import Any


class ParameterParser:
    """参数解析器基类."""

    def parse(self, value: str) -> Any:
        raise NotImplementedError


class BboxParser(ParameterParser):
    """解析bbox参数: '<bbox>x1 y1 x2 y2</bbox>' -> ((x1+x2)/2, (y1+y2)/2)."""

    def parse(self, value: str) -> tuple:
        pattern = r"<bbox>(\d+)\s+(\d+)\s+(\d+)\s+(\d+)</bbox>"
        match = re.search(pattern, value)
        if not match:
            raise ValueError(f"Invalid bbox format: {value}")
        return self.get_center(tuple(map(int, match.groups())))

    def get_center(self, bbox: tuple) -> tuple:
        """获取bbox的中心点坐标."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)


class PointParser(ParameterParser):
    """解析point参数: '<point>x y</point>' -> (x, y)."""

    def parse(self, value: str) -> tuple:
        pattern = r"<point>(\d+)\s+(\d+)</point>"
        match = re.search(pattern, value)
        if not match:
            raise ValueError(f"Invalid point format: {value}")
        return tuple(map(int, match.groups()))


class LocationParser(ParameterParser):
    """智能定位解析器，支持bbox和point两种格式."""

    def parse(self, value: str) -> tuple:
        # 优先尝试bbox格式
        if "<bbox>" in value:
            bbox_parser = BboxParser()
            bbox = bbox_parser.parse(value)
            return bbox_parser.get_center(bbox)

        # 尝试point格式
        if "<point>" in value:
            point_parser = PointParser()
            return point_parser.parse(value)

        raise ValueError(f"Unsupported location format: {value}. Use <bbox>x1 y1 x2 y2</bbox> or <point>x y</point>")


class DurationParser(ParameterParser):
    """解析duration参数，设置默认值和范围限制."""

    def __init__(self, default=2, min_val=1, max_val=3) -> None:
        self.default = default
        self.min_val = min_val
        self.max_val = max_val

    def parse(self, value: str) -> int:
        if not value or value == "t":
            return self.default
        try:
            duration = int(value)
            return max(self.min_val, min(duration, self.max_val))
        except ValueError:
            return self.default


class CountParser(ParameterParser):
    """解析count参数."""

    def __init__(self, default=1, min_val=1, max_val=3) -> None:
        self.default = default
        self.min_val = min_val
        self.max_val = max_val

    def parse(self, value: str) -> int:
        if not value or value == "x":
            return self.default
        try:
            count = int(value)
            return max(self.min_val, min(count, self.max_val))
        except ValueError:
            return self.default


def mobile_tool(
    name: str,
    description: str,
    parameters: str,
    parsers: dict[str, ParameterParser] | None = None,
):
    """装饰器，用于标记mobile工具方法并自动处理参数解析.

    Args:
        prompt: 工具的prompt描述，用于生成list_prompt_tools
        parsers: 参数解析器字典 {参数名: 解析器}

    Example:
        @mobile_tool(
            name="tap",
            description="Tap the screen at the given coordinates.",
            parameters="(start_box='<bbox>x1 y1 x2 y2</bbox>')",
            parsers={'start_box': BboxParser()}
        )
        async def tap(self, start_box: str) -> None:
            x, y = self._parse_bbox_center(start_box)
            # 实际实现...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 获取函数签名进行参数映射
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # 如果有解析器，则进行参数解析
            if parsers:
                for param_name, parser in parsers.items():
                    if param_name in bound_args.arguments:
                        original_value = bound_args.arguments[param_name]
                        if isinstance(original_value, str):
                            bound_args.arguments[param_name] = parser.parse(original_value)

            # 调用原方法
            return await func(**bound_args.arguments)

        # 将工具信息直接绑定到方法上，避免全局变量
        wrapper._mobile_tool_info = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "parsers": parsers or {},
            "method_name": func.__name__,
        }

        return wrapper

    return decorator


class MobileToolMixin:
    """提供mobile工具相关的mixin方法."""

    def get_mobile_tools_prompt(self) -> str:
        """自动生成当前实例的mobile工具prompt列表."""
        prompts = []

        # 遍历当前实例的所有方法
        for method_name in dir(self):
            method = getattr(self, method_name)

            # 检查是否有mobile_tool装饰器信息
            if hasattr(method, "_mobile_tool_info"):
                tool_info = method._mobile_tool_info
                prompts.append(f"{tool_info['name']}{tool_info['parameters']} # {tool_info['description']}")

        return "\n".join(prompts)
