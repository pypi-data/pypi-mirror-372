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

import base64
import json
import logging
from typing import Any

from mobile_use_sdk.utils.image import (
    get_base64_from_url,
    get_dimensions_from_url,
)
from mobile_use_sdk.volcengine_openapi.acep_httpx_client import ACEPHttpxClient

logger = logging.getLogger(__name__)


class ACEP_API:
    def __init__(self, ak: str, sk: str, account_id: str) -> None:
        self.client = ACEPHttpxClient(ak, sk, account_id=account_id)

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_value, traceback):
        self.aclose()

    async def aclose(self) -> None:
        await self.client.aclose()

    async def auto_install_app(self, product_id: str, pod_id: str, download_url: str) -> dict[str, Any]:
        params = {
            "ProductId": product_id,
            "PodIdList": [pod_id],
            "DownloadUrl": download_url,
        }
        return await self.client.call_acep_api_async("AutoInstallApp", params=params)

    async def launch_app(self, product_id: str, pod_id: str, package_name: str) -> dict[str, Any]:
        params = {
            "ProductId": product_id,
            "PodIdList": [pod_id],
            "PackageName": package_name,
        }
        return await self.client.call_acep_api_async("LaunchApp", params=params)

    async def close_app(self, product_id: str, pod_id: str, package_name: str) -> dict[str, Any]:
        params = {
            "ProductId": product_id,
            "PodIdList": [pod_id],
            "PackageName": package_name,
        }
        return await self.client.call_acep_api_async("CloseApp", params=params)

    async def get_pod_app_list(self, product_id: str, pod_id: str) -> dict[str, Any]:
        params = {
            "ProductId": product_id,
            "PodId": pod_id,
        }
        return await self.client.call_acep_api_async("GetPodAppList", params=params, http_method="GET")

    def _extract_result_content_from_run_sync_command(self, api_response: dict[str, Any]) -> str:
        # 处理 RunSyncCommand 的响应格式
        if "Status" in api_response and len(api_response["Status"]) > 0:
            status = api_response["Status"][0]
            if "Detail" in status:
                detail = status["Detail"] or ""
            if "Success" in status:
                if not status["Success"]:
                    return f"执行命令失败 {detail}"
                return detail

        return "执行命令失败"

    async def run_sync_command(
        self,
        product_id: str,
        pod_id: str,
        command: str,
        permission_type: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "ProductId": product_id,
            "PodIdList": [pod_id],
            "Command": command,
        }
        if permission_type:
            params["PermissionType"] = permission_type

        response = await self.client.call_acep_api_async("RunSyncCommand", params=params)
        if not response.get("is_success"):
            return {
                "is_success": False,
                "message": f"执行命令失败 {response.get('error_message')}",
            }

        command_result = self._extract_result_content_from_run_sync_command(response.get("result"))

        return {"is_success": True, "message": command_result}

    # ==================== 高级操作方法 (基于 RunSyncCommand) ====================

    # Android 按键码常量
    KEYCODE_HOME = 3
    KEYCODE_BACK = 4
    KEYCODE_MENU = 82

    # 默认滑动持续时间
    DEFAULT_SWIPE_DURATION = 300

    async def tap(self, product_id: str, pod_id: str, x: int, y: int) -> dict[str, Any]:
        """异步点击屏幕.

        Args:
            product_id: 产品 ID
            pod_id: Pod ID
            x: X 坐标
            y: Y 坐标

        Returns:
            API 响应结果
        """
        command = f"input tap {x} {y}"
        return await self.run_sync_command(product_id, pod_id, command)

    async def swipe(
        self,
        product_id: str,
        pod_id: str,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration: int = DEFAULT_SWIPE_DURATION,
    ) -> dict[str, Any]:
        command = f"input swipe {from_x} {from_y} {to_x} {to_y} {duration}"
        return await self.run_sync_command(product_id, pod_id, command)

    async def long_press(self, product_id: str, pod_id: str, x: int, y: int, duration: int = 1000) -> dict[str, Any]:
        # 长按通过滑动到同一位置实现
        command = f"input swipe {x} {y} {x} {y} {duration}"
        return await self.run_sync_command(product_id, pod_id, command)

    async def input_text(self, product_id: str, pod_id: str, text: str) -> dict[str, Any]:
        # 使用 base64 编码文本
        encoded_text = base64.b64encode(text.encode("utf-8")).decode("ascii")
        command = f'am broadcast -a device.gameservice.keyevent.value --es value "$(echo {encoded_text} | base64 -d)"'
        return await self.run_sync_command(product_id, pod_id, command)

    async def clear_text(self, product_id: str, pod_id: str) -> dict[str, Any]:
        command = "am broadcast -a device.gameservice.keyevent.clear"
        return await self.run_sync_command(product_id, pod_id, command)

    async def press_home(self, product_id: str, pod_id: str) -> dict[str, Any]:
        command = f"input keyevent {self.KEYCODE_HOME}"
        return await self.run_sync_command(product_id, pod_id, command)

    async def press_back(self, product_id: str, pod_id: str, count: int = 1) -> dict[str, Any]:
        # 如果需要多次按键，可以发送多个命令或使用循环
        if count == 1:
            command = f"input keyevent {self.KEYCODE_BACK}"
            response = await self.run_sync_command(product_id, pod_id, command)
        else:
            # 多次按键，这里简化处理，发送最后一次的结果
            for _ in range(count):
                command = f"input keyevent {self.KEYCODE_BACK}"
                response = await self.run_sync_command(product_id, pod_id, command)
        return response

    async def press_menu(self, product_id: str, pod_id: str) -> dict[str, Any]:
        command = f"input keyevent {self.KEYCODE_MENU}"
        return await self.run_sync_command(product_id, pod_id, command)

    async def screenshot(
        self,
        product_id: str,
        pod_id: str,
        tos_config: str,
        use_base64_screenshot: bool = False,
    ) -> dict[str, Any]:
        command = f"cap_tos -tos_conf '{tos_config}'"
        # TODO  等待云手机更新
        # command = f'cap_tos -tos_conf "{tos_config}" -command screenshot'
        result = await self.run_sync_command(product_id, pod_id, command)
        if not result.get("is_success"):
            raise ValueError("Screenshot URL is empty")

        result_text = result.get("message")
        got_base64 = False

        screenshot_url = ""
        width = 0
        height = 0

        # handle v1 格式: ScreenshotURL: https://xxx
        if result_text.startswith("ScreenshotURL: "):
            screenshot_url = result_text.replace("ScreenshotURL: ", "").strip()
            # v1 格式没有分辨率信息，需要从图片获取
            (
                width,
                height,
                screenshot_url,
            ) = await get_dimensions_from_url(screenshot_url, use_base64_screenshot)
            got_base64 = True
        else:
            # handle v2 格式: JSON 格式
            try:
                parsed_data = json.loads(result_text)
                screenshot_url = parsed_data.get("screenshot_url", "")
                if not screenshot_url:
                    raise ValueError("screenshot_url is empty")

                # 优先使用 resolution 字段
                if parsed_data.get("resolution", ""):
                    resolution_parts = parsed_data["resolution"].split("x")
                    if len(resolution_parts) == 2:
                        width = int(resolution_parts[0]) if resolution_parts[0] else 0
                        height = int(resolution_parts[1]) if resolution_parts[1] else 0
                else:
                    # 兼容老的 width/height 字段
                    width = int(parsed_data.get("width", 0))
                    height = int(parsed_data.get("height", 0))

                if width <= 0 or height <= 0:
                    (
                        width,
                        height,
                        screenshot_url,
                    ) = await get_dimensions_from_url(screenshot_url, use_base64_screenshot)
                    got_base64 = True
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                raise ValueError(f"Failed to parse screenshot result: {e}, output: {result_text}")

        if not screenshot_url:
            raise ValueError("Screenshot URL is empty")

        if not got_base64 and use_base64_screenshot:
            screenshot_url = await get_base64_from_url(screenshot_url)

        return {
            "screenshot": screenshot_url,
            "screenshot_dimensions": (width, height),
        }

    # async def ui_dump(
    #     self, product_id: str, pod_id: str, tos_config: str
    # ) -> Dict[str, Any]:
    #     command = f'cap_tos -tos_conf "{tos_config}" -command uiautomator_dump'
    #     return await self.run_sync_command(product_id, pod_id, command)

    # ==================== 便捷的应用操作方法 ====================

    async def launch_app_simple(self, product_id: str, pod_id: str, package_name: str) -> str:
        response = await self.launch_app(product_id, pod_id, package_name)
        if not response.get("is_success"):
            raise ValueError(f"启动应用失败: {response.get('error_message', '未知错误')}")
        return response

    async def close_app_simple(self, product_id: str, pod_id: str, package_name: str) -> str:
        response = await self.close_app(product_id, pod_id, package_name)
        if not response.get("is_success"):
            raise ValueError(f"关闭应用失败: {response.get('error_message', '未知错误')}")
        return response

    async def list_apps_simple(self, product_id: str, pod_id: str) -> list[dict[str, str]]:
        result = await self.get_pod_app_list(product_id, pod_id)
        if not result.get("is_success"):
            raise ValueError(f"获取应用列表失败: {result.get('error_message', '未知错误')}")

        # 解析应用列表
        app_list = result.get("result", {}).get("Row", [])
        simplified_apps = []

        for app in app_list:
            app_info = {
                "app_name": app.get("AppName", ""),
                "package_name": app.get("PackageName", ""),
                "app_id": app.get("AppID", ""),
                "install_status": app.get("InstallStatus", ""),
            }
            simplified_apps.append(app_info)

        return simplified_apps

    async def detail_pod(self, product_id: str, pod_id: str) -> dict[str, Any]:
        """获取 Pod 详细信息.

        Args:
            product_id: 产品 ID
            pod_id: Pod ID

        Returns:
            API 响应结果
        """
        params = {
            "ProductId": product_id,
            "PodId": pod_id,
        }
        return await self.client.call_acep_api_async("DetailPod", params=params, http_method="GET")

    async def detail_display_layout_mini(self, product_id: str, display_layout_id: str) -> dict[str, Any]:
        """获取显示布局详细信息.

        Args:
            product_id: 产品 ID
            display_layout_id: 显示布局 ID

        Returns:
            API 响应结果
        """
        params = {
            "ProductId": product_id,
            "DisplayLayoutId": display_layout_id,
        }
        return await self.client.call_acep_api_async("DetailDisplayLayoutMini", params=params, http_method="GET")
