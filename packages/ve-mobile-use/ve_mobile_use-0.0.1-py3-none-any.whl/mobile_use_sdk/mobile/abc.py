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

from abc import ABC, abstractmethod


class Mobile(ABC):
    """Abstract base class for mobile tools."""

    @abstractmethod
    async def tap(self, point: tuple[int, int]) -> str:
        """Tap the screen at the given coordinates."""
        pass

    @abstractmethod
    async def swipe(
        self,
        start_point: tuple[int, int],
        end_point: tuple[int, int],
        duration: int = 1000,
    ) -> str:
        """Swipe the screen from the given coordinates to the given coordinates for the given duration."""
        pass

    @abstractmethod
    async def long_press(self, point: tuple[int, int], duration: int = 1000) -> str:
        """Long press the screen at the given coordinates for the given duration."""
        pass

    @abstractmethod
    async def input_text(self, text: str) -> str:
        """Type the given text on the screen."""
        pass

    @abstractmethod
    async def press_home(self) -> str:
        """Press the home button."""
        pass

    @abstractmethod
    async def press_back(self, count: int = 1) -> str:
        """Press the back button."""

    @abstractmethod
    async def screenshot(self) -> dict:
        """Take a screenshot of the screen.

        return: {
            "screenshot": str,
            "screenshot_dimensions": (width, height),
        }
        """
        pass

    def is_mobile_tool(self, name: str) -> bool:
        """检查给定的工具名称是否是mobile工具."""
        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, "_mobile_tool_info"):
                tool_info = method._mobile_tool_info
                if tool_info["name"] == name:
                    return True
        return False
