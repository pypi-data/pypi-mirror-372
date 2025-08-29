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

import logging
import urllib.parse
from typing import Any

import httpx

from .acep_signer import ACEP_Signer, VolcEngineOpenAPISigner

logger = logging.getLogger(__name__)


class ACEPHttpxClient:
    """基于自定义签名器的 httpx 异步客户端.

    这个类使用自定义的火山引擎OpenAPI签名器，
    使用 httpx 进行异步 HTTP 请求。
    """

    DEFAULT_VERSION = "2023-10-30"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_HTTP_METHOD = "POST"

    def __init__(self, ak: str, sk: str, account_id: str) -> None:
        self.acep_signer = ACEP_Signer(ak, sk, account_id)
        self.signer = VolcEngineOpenAPISigner(self.acep_signer.account_info)
        # 创建 httpx 异步客户端
        self.http_client = httpx.AsyncClient(
            timeout=self.DEFAULT_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self) -> None:
        """关闭 httpx 客户端."""
        await self.http_client.aclose()

    def _encode_params(self, params: dict[str, Any]) -> str:
        """正确编码参数，处理list类型."""
        encoded_parts = []
        for key in sorted(params.keys()):
            if isinstance(params[key], list):
                # 对于list类型，为每个元素生成一个参数
                for item in params[key]:
                    encoded_key = urllib.parse.quote(str(key), safe="-_.~")
                    encoded_value = urllib.parse.quote(str(item), safe="-_.~")
                    encoded_parts.append(f"{encoded_key}={encoded_value}")
            else:
                # 单个值直接编码
                encoded_key = urllib.parse.quote(str(key), safe="-_.~")
                encoded_value = urllib.parse.quote(str(params[key]), safe="-_.~")
                encoded_parts.append(f"{encoded_key}={encoded_value}")

        return "&".join(encoded_parts).replace("+", "%20")

    def _prepare_httpx_request(
        self,
        action: str,
        version: str,
        http_method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if params is None:
            params = {}

        # 构造查询参数和请求体
        if http_method == "GET":
            # GET 请求：所有参数都在 query 中
            query_params = {"Action": action, "Version": version, **params}
            body = ""
        else:
            # POST 请求：Action 和 Version 在 query 中，其他参数在 body 中
            query_params = {"Action": action, "Version": version}

            # 将参数编码为 application/x-www-form-urlencoded 格式
            # 需要正确处理list类型参数，避免包含数组括号
            body = self._encode_params(params) if params else ""

        # 使用新的签名接口
        signed_request = self.signer.sign_request(method=http_method, query_params=query_params, body=body)

        # 构造 httpx 请求参数
        httpx_params = {
            "method": signed_request["method"],
            "url": signed_request["url"],
            "headers": signed_request["headers"],
        }

        # 如果有请求体，添加到请求中
        if signed_request["body"]:
            httpx_params["data"] = signed_request["body"]

        return httpx_params

    async def call_acep_api_async(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        http_method: str = DEFAULT_HTTP_METHOD,
        version: str = DEFAULT_VERSION,
    ) -> dict[str, Any]:
        if params is None:
            params = {}

        try:
            # 使用自定义签名器生成完整的签名请求参数
            httpx_params = self._prepare_httpx_request(
                action=action, version=version, http_method=http_method, params=params
            )

            # 使用 httpx 发送异步请求
            response = await self.http_client.request(**httpx_params, timeout=self.DEFAULT_TIMEOUT)

            response.raise_for_status()
            response_json: dict = response.json()
            error_message = response_json.get("ResponseMetadata", {}).get("Error", {}).get("Message", "")
            if error_message:
                return {"is_success": False, "error_message": error_message}
            return {"is_success": True, "result": response_json.get("Result")}

        except Exception as e:
            logger.exception(f"Request failed: {type(e).__name__}: {e!s}")
            return {"is_success": False, "error_message": f"{type(e).__name__}: {e!s}"}
