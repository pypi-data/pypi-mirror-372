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

from mobile_use_sdk.agent.tools.tool.abc import Tool


class WaitTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="wait",
            description="Sleep for t seconds number, wait for change,  t is lower than 10, higher than 0.",
            parameters={
                "type": "object",
                "required": ["t"],
                "properties": {
                    "t": {
                        "type": "number",
                        "description": "The time to wait in seconds",
                    },
                },
            },
        )

    async def handler(self, args: dict) -> str:
        t = float(args.get("t"))
        await asyncio.sleep(t)
        return f"已等待{args.get('t')}s"
