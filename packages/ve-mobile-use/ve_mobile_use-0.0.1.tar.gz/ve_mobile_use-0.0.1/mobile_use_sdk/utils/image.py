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
import base64
from io import BytesIO

import httpx
from PIL import Image


async def get_dimensions_from_url(screenshot_url: str, use_base64_screenshot: bool = False) -> tuple[int, int, str]:
    """更新截图的尺寸信息."""
    try:
        # 下载图片
        async with httpx.AsyncClient() as client:
            response = await client.get(screenshot_url)
            if response.is_error:
                return (0, 0, "")
            # 使用 PIL 获取图片尺寸
            image = Image.open(BytesIO(response.content))
            url = get_base64_from_bytes(response.content) if use_base64_screenshot else screenshot_url
            width, height = image.size
            image.close()
            return (width, height, url)
    except Exception:
        raise


def get_base64_from_bytes(content: bytes) -> str:
    """获取图片的 base64 编码."""
    mime_type = "image/png"
    base64_data = base64.b64encode(content).decode("ascii")
    return f"data:{mime_type};base64,{base64_data}"


async def get_base64_from_url(screenshot_url: str, retry_count: int = 0) -> str:
    """获取图片的 base64 编码."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(screenshot_url)
            if response.is_error:
                if retry_count >= 3:
                    raise ValueError("获取图片的 base64 编码失败")
                await asyncio.sleep(1)
                return await get_base64_from_url(screenshot_url, retry_count + 1)
            return get_base64_from_bytes(response.content)
    except Exception:
        raise
