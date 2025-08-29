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
import json
from typing import Any

from mobile_use_sdk.config.config import TosInfo
from mobile_use_sdk.mobile.abc import Mobile
from mobile_use_sdk.utils.bbox import regular_bbox_xy_for_ui_tars
from mobile_use_sdk.volcengine_openapi import ACEP_API

from ..decorators import (
    BboxParser,
    CountParser,
    DurationParser,
    MobileToolMixin,
    mobile_tool,
)


class CloudPhone(Mobile, MobileToolMixin):
    """基于 ACEPHttpxClient 的云手机操作客户端.

    使用 HTTP API 调用 ACEP 服务
    """

    def __init__(
        self,
        ak: str,
        sk: str,
        account_id: str,
        tos_info: TosInfo | None = TosInfo(),
    ) -> None:
        self.acep_client: ACEP_API | None = None
        self.acep_ak = ak
        self.acep_sk = sk
        self.account_id = account_id
        self.tos_info: TosInfo = tos_info

        self.product_id: str = ""
        self.pod_id: str = ""

        self.tos_config: str = ""
        self.use_base64_screenshot = False
        self._apps_list: list[dict] | None = None
        self.phone_width: int = 720
        self.phone_height: int = 1280

    async def initialize(
        self,
        pod_id: str,
        product_id: str,
    ):
        """初始化云手机客户端.

        Args:
            pod_id: Pod ID
            product_id: 产品 ID
        """
        self.product_id = product_id
        self.pod_id = pod_id

        # 初始化 ACEP HTTP 客户端
        self.acep_client = ACEP_API(self.acep_ak, self.acep_sk, account_id=self.account_id)

        tos_config_dict = {
            "AccessKey": self.tos_info.ak,
            "SecretKey": self.tos_info.sk,
            "SessionToken": "",
            "Bucket": self.tos_info.bucket,
            "Region": self.tos_info.region,
            "Endpoint": self.tos_info.endpoint,
        }
        tos_json = json.dumps(tos_config_dict)
        self.tos_config = base64.b64encode(tos_json.encode("utf-8")).decode("utf-8")

        return self

    def change_config(self, use_base64_screenshot: bool | None = None) -> None:
        if use_base64_screenshot is not None:
            self.use_base64_screenshot = use_base64_screenshot

    async def aclose(self) -> None:
        """关闭客户端."""
        if self.acep_client:
            await self.acep_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    # ==================== 基础操作方法 ====================

    async def tap(self, point: tuple[int, int]) -> str:
        """点击屏幕指定坐标."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.tap(self.product_id, self.pod_id, point[0], point[1])
        if not response.get("is_success"):
            raise ValueError(f"点击失败: {response.get('message', '未知错误')}")
        return response.get("message", "点击操作成功")

    async def swipe(
        self,
        start_point: tuple[int, int],
        end_point: tuple[int, int],
    ) -> str:
        """滑动屏幕."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.swipe(
            self.product_id,
            self.pod_id,
            start_point[0],
            start_point[1],
            end_point[0],
            end_point[1],
        )
        if not response.get("is_success"):
            raise ValueError(f"滑动失败: {response.get('message', '未知错误')}")
        return response.get("message", "滑动操作成功")

    async def long_press(self, point: tuple[int, int], duration: int = 1) -> str:
        """长按屏幕."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.long_press(self.product_id, self.pod_id, point[0], point[1], duration * 1000)
        if not response.get("is_success"):
            raise ValueError(f"长按失败: {response.get('message', '未知错误')}")
        return response.get("message", "长按操作成功")

    async def input_text(self, text: str) -> str:
        """输入文本."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.input_text(self.product_id, self.pod_id, text)
        if not response.get("is_success"):
            raise ValueError(f"文本输入失败: {response.get('message', '未知错误')}")
        return response.get("message", "文本输入成功")

    async def press_home(self) -> str:
        """按 Home 键."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.press_home(self.product_id, self.pod_id)
        if not response.get("is_success"):
            raise ValueError(f"Home键操作失败: {response.get('message', '未知错误')}")
        return response.get("message", "Home键操作成功")

    async def press_back(self, count: int = 1) -> str:
        """按 Back 键."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        response = await self.acep_client.press_back(self.product_id, self.pod_id, count)
        if not response.get("is_success"):
            raise ValueError(f"Back键操作失败: {response.get('message', '未知错误')}")
        return response.get("message", "Back键操作成功")

    async def screenshot(self) -> dict:
        """截屏."""
        screenshot_state = await self._screenshot()
        # 处理横竖屏切换逻辑
        self._change_phone_dimensions(
            screenshot_state.get("screenshot_dimensions")[0],
            screenshot_state.get("screenshot_dimensions")[1],
        )
        return screenshot_state

    # ==================== Mobile Tool 装饰器方法 ====================

    # @mobile_tool(
    #     name="ui_dump",
    #     parameters="()",
    #     description="use uiautomator dump to export the current screen to a xml.",
    # )
    # async def ui_dump(self) -> str:
    #     """获取 UI 信息"""
    #     if not self.acep_client:
    #         raise ValueError("Client is not initialized")

    #     response = await self.acep_client.ui_dump(
    #         self.product_id, self.pod_id, self.tos_config
    #     )
    #     content = response

    #     # 解析 UI dump 结果，模拟 MCP 的响应格式
    #     try:
    #         # 假设响应中包含 elements 数组（需要根据实际 API 响应调整）
    #         result_data = self._parse_json_response(content)
    #         elements = result_data.get("elements", [])

    #         if not elements:
    #             return "No elements found"

    #         # 格式化元素数据，保持与 MCP 版本一致
    #         formatted_elements = [
    #             {
    #                 "resource_id": element.get("resource_id", ""),
    #                 "class": element.get("class_name", ""),
    #                 "text": element.get("text", ""),
    #                 "content_desc": element.get("content_desc", ""),
    #                 "clickable": element.get("clickable", ""),
    #                 "checkable": element.get("checkable", ""),
    #                 "checked": element.get("checked", ""),
    #                 "enabled": element.get("enabled", ""),
    #                 "password": element.get("password", ""),
    #                 "selected": element.get("selected", ""),
    #             }
    #             for element in elements
    #         ]
    #         return f"xml_json:\n{json.dumps(formatted_elements, ensure_ascii=False, indent=2)}"
    #     except Exception:
    #         # 如果解析失败，返回原始内容
    #         return content

    @mobile_tool(
        name="tap",
        parameters="(start_box='<bbox>x1 y1 x2 y2</bbox>')",
        description="Tap the screen at the given coordinates.",
        parsers={"start_box": BboxParser()},
    )
    async def tap_bbox(self, start_box: tuple[int, int]) -> str:
        """使用 bbox 格式点击屏幕."""
        x, y = regular_bbox_xy_for_ui_tars(
            *start_box,
            width=self.phone_width,
            height=self.phone_height,
        )
        await self.tap((x, y))
        return f"已成功点击坐标 ({x}, {y})"

    @mobile_tool(
        name="swipe",
        parameters="(start_box='<bbox>x1 y1 x2 y2</bbox>', end_box='<bbox>x3 y3 x4 y4</bbox>')",
        description="Swipe the screen from the given coordinates to the given coordinates",
        parsers={
            "start_box": BboxParser(),
            "end_box": BboxParser(),
        },
    )
    async def swipe_bbox(self, start_box: tuple[int, int], end_box: tuple[int, int]) -> str:
        """使用 bbox 格式滑动屏幕."""
        x1, y1 = regular_bbox_xy_for_ui_tars(
            *start_box,
            width=self.phone_width,
            height=self.phone_height,
        )
        x2, y2 = regular_bbox_xy_for_ui_tars(
            *end_box,
            width=self.phone_width,
            height=self.phone_height,
        )
        await self.swipe((x1, y1), (x2, y2))
        return f"已成功滑动从 ({x1}, {y1}) 到 ({x2}, {y2})"

    @mobile_tool(
        name="long_press",
        parameters="(start_box='<bbox>x1 y1 x2 y2</bbox>', duration='t')",
        description="Long press the screen at the given coordinates for the given duration. t is lower than 3s, higher than 1s.",
        parsers={
            "start_box": BboxParser(),
            "duration": DurationParser(),
        },
    )
    async def long_press_bbox(self, start_box: tuple[int, int], duration: int = 2) -> str:
        """使用 bbox 格式长按屏幕."""
        x, y = regular_bbox_xy_for_ui_tars(
            *start_box,
            width=self.phone_width,
            height=self.phone_height,
        )
        await self.long_press((x, y), duration)
        return f"已成功长按坐标 ({x}, {y}) {duration} 秒"

    @mobile_tool(
        name="type",
        parameters="(content='')",
        description="Type the given text on the screen. If you want to type, must check keyboard is open, or you must tap the input field to open keyboard.",
    )
    async def input_text_tool(self, content: str) -> str:
        """文本输入工具方法."""
        await self.input_text(content)
        return f"已成功输入文本: '{content}'"

    @mobile_tool(
        name="press_home",
        parameters="()",
        description="Go to the home page",
    )
    async def press_home_tool(self) -> str:
        """Home 键工具方法."""
        await self.press_home()
        return "已成功按下 Home 键"

    @mobile_tool(
        name="press_back",
        parameters="(count='x')",
        description="Go back to the previous page,x is the number of times to press the back key, default is 1, min is 1, max is 3.",
        parsers={"count": CountParser(default=1, min_val=1, max_val=3)},
    )
    async def press_back_tool(self, count: int = 1) -> str:
        """Back 键工具方法."""
        await self.press_back(count)
        return f"已成功按下 Back 键 {count} 次"

    @mobile_tool(
        name="launch_app",
        parameters="(package_name='')",
        description="Launch the app with the given package name.",
    )
    async def launch_app(self, package_name: str) -> str:
        """启动应用."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        await self.acep_client.launch_app_simple(self.product_id, self.pod_id, package_name)
        return f"已成功启动应用 {package_name}"

    @mobile_tool(
        name="close_app",
        parameters="(package_name='')",
        description="Close the app with the given package name.",
    )
    async def close_app(self, package_name: str) -> str:
        """关闭应用."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        await self.acep_client.close_app_simple(self.product_id, self.pod_id, package_name)
        return f"已成功关闭应用 {package_name}"

    @mobile_tool(
        name="list_apps",
        parameters="()",
        description="List all installed apps, return a list of app_name and package_name.",
    )
    async def list_apps_str(self) -> str:
        app_list = await self.list_apps(use_cache=False)
        if len(app_list) == 0:
            return """successfully get app list: No installed app found. use cloud phone console to some app first."""
        return f"""successfully get app list:\n
    {", ".join(f"{app['app_name']}: {app['package_name']}" for app in app_list)}\n\n"""

    # ==================== 辅助方法 ====================

    async def list_apps(self, use_cache: bool = True) -> list[dict]:
        """获取应用列表."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        # 使用缓存
        if self._apps_list and use_cache:
            return self._apps_list

        try:
            apps = await self.acep_client.list_apps_simple(self.product_id, self.pod_id)

            # 转换为与 MCP 版本一致的格式
            self._apps_list = [{"app_name": app["app_name"], "package_name": app["package_name"]} for app in apps]
            return self._apps_list
        except Exception as e:
            raise ValueError(f"获取应用列表失败: {e!s}")

    async def clear_apps(self) -> str:
        """清除所有已打开的应用."""
        apps = await self.list_apps()
        for app in apps:
            await self.close_app(app.get("package_name"))
        return "All apps cleared"

    async def auto_install_app(self, app_name: str) -> str:
        """自动安装应用（待实现）."""
        # TODO: 实现应用安装逻辑
        pass

    async def get_resolution(self) -> tuple[int, int]:
        """获取 Pod 的实际分辨率.

        Returns:
            (width, height) 元组
        """
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        # 获取 Pod 详细信息
        pod_response = await self.acep_client.detail_pod(self.product_id, self.pod_id)
        if not pod_response.get("is_success"):
            raise ValueError(f"获取 Pod 详情失败: {pod_response.get('error_message', '未知错误')}")

        pod_result = pod_response.get("result", {})
        display_layout_id = pod_result.get("DisplayLayoutId")

        if not display_layout_id:
            raise ValueError("获取 Pod 详情失败: DisplayLayoutId 为空")

        # 获取显示布局详细信息
        layout_response = await self.acep_client.detail_display_layout_mini(self.product_id, display_layout_id)
        if not layout_response.get("is_success"):
            raise ValueError(f"获取显示布局详情失败: {layout_response.get('error_message', '未知错误')}")

        layout_result = layout_response.get("result", {})
        width = layout_result.get("Width")
        height = layout_result.get("Height")

        if width is None or height is None:
            raise ValueError("获取显示布局详情失败: 宽度或高度为空")

        # 更新内部存储的分辨率
        self.phone_width = width
        self.phone_height = height

        return width, height

    def _change_phone_dimensions(self, width: int, height: int) -> None:
        """更新手机屏幕尺寸."""
        if width != 0:
            self.phone_width = width
        if height != 0:
            self.phone_height = height

    async def _screenshot(self) -> dict:
        """内部截屏方法，支持重试."""
        if not self.acep_client:
            raise ValueError("Client is not initialized")

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                return await self.acep_client.screenshot(
                    self.product_id,
                    self.pod_id,
                    self.tos_config,
                    use_base64_screenshot=self.use_base64_screenshot,
                )

                # acep_client.screenshot 已经在内部处理了 is_success 检查
                # 如果失败会直接抛出 ValueError，所以这里直接返回成功的结果

            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise ValueError(f"截图失败，已重试 {max_retries} 次。最后错误: {e}")
                await asyncio.sleep(1)  # 等待1秒后重试

        # 如果所有重试都失败
        raise ValueError(f"截图失败，已重试 {max_retries} 次")
