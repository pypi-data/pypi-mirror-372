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


class Tool(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        is_special_tool: bool | None = False,
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters
        self.is_special_tool = is_special_tool

    async def call(self, args: dict | None = None) -> str:
        if args is None:
            args = {}
        result = await self.handler(args)
        if result is None:
            return ""
        return result

    @abstractmethod
    async def handler(self, args: dict | None = None) -> str | None:
        pass

    def get_tool_schema_for_openai(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class SpecialTool(Tool):
    def __init__(self, name: str, description: str, parameters: dict) -> None:
        super().__init__(name, description, parameters, is_special_tool=True)

    def special_message(self, content: str, args: dict) -> str | None:
        pass

    def special_memory(self, content: str | None = None) -> str | None:
        pass
