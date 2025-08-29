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

import hashlib
import hmac
import urllib.parse
from datetime import UTC, datetime
from typing import Any

from mobile_use_sdk.config import VolcEngineAuth


class VolcEngineOpenAPISigner:
    """火山引擎OpenAPI签名器.

    基于官方示例实现HMAC-SHA256签名算法
    """

    def __init__(self, account_info: VolcEngineAuth) -> None:
        """初始化签名器."""
        self.account_info = account_info
        self.service = "acep"
        self.region = "cn-north-1"
        self.host = "open.volcengineapi.com"
        self.algorithm = "HMAC-SHA256"
        self.content_type = "application/x-www-form-urlencoded"

    def _norm_query(self, params: dict[str, Any]) -> str:
        """规范化查询字符串（按照官方示例）."""
        if not params:
            return ""

        query = ""
        for key in sorted(params.keys()):
            if isinstance(params[key], list):
                for k in params[key]:
                    query = (
                        query
                        + urllib.parse.quote(key, safe="-_.~")
                        + "="
                        + urllib.parse.quote(str(k), safe="-_.~")
                        + "&"
                    )
            else:
                query = (
                    query
                    + urllib.parse.quote(key, safe="-_.~")
                    + "="
                    + urllib.parse.quote(str(params[key]), safe="-_.~")
                    + "&"
                )
        query = query[:-1]
        return query.replace("+", "%20")

    def _hmac_sha256(self, key: bytes, content: str) -> bytes:
        """HMAC-SHA256加密."""
        return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()

    def _hash_sha256(self, content: str) -> str:
        """SHA256哈希算法."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def sign_request(
        self,
        method: str,
        query_params: dict[str, Any],
        body: str = "",
        additional_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """签名请求（按照官方示例逻辑）.

        Args:
            method: HTTP方法（GET/POST）
            query_params: 查询参数（不包含Action和Version，会自动添加）
            body: 请求体
            additional_headers: 额外的请求头

        Returns:
            包含完整请求信息的字典
        """
        if additional_headers is None:
            additional_headers = {}

        # 获取当前时间
        now = datetime.now(UTC)
        x_date = now.strftime("%Y%m%dT%H%M%SZ")
        short_x_date = x_date[:8]

        # 计算body的SHA256哈希
        x_content_sha256 = self._hash_sha256(body)

        # 构造请求头
        headers = {
            "Host": self.host,
            "X-Content-Sha256": x_content_sha256,
            "X-Date": x_date,
            "Content-Type": self.content_type,
            **additional_headers,
        }

        # 固定的签名头部顺序（按照官方示例）
        signed_headers_list = ["content-type", "host", "x-content-sha256", "x-date"]
        signed_headers_str = ";".join(signed_headers_list)

        # 构造规范请求字符串
        canonical_request_str = "\n".join(
            [
                method.upper(),
                "/",
                self._norm_query(query_params),
                "\n".join(
                    [
                        "content-type:" + self.content_type,
                        "host:" + self.host,
                        "x-content-sha256:" + x_content_sha256,
                        "x-date:" + x_date,
                    ]
                ),
                "",
                signed_headers_str,
                x_content_sha256,
            ]
        )

        # 计算规范请求的哈希
        hashed_canonical_request = self._hash_sha256(canonical_request_str)

        # 构造凭证范围
        credential_scope = f"{short_x_date}/{self.region}/{self.service}/request"

        # 构造待签名字符串
        string_to_sign = f"{self.algorithm}\n{x_date}\n{credential_scope}\n{hashed_canonical_request}"

        # 计算签名（按照官方示例，直接使用secret_key，不添加前缀）
        k_date = self._hmac_sha256(self.account_info.sk.encode("utf-8"), short_x_date)
        k_region = self._hmac_sha256(k_date, self.region)
        k_service = self._hmac_sha256(k_region, self.service)
        k_signing = self._hmac_sha256(k_service, "request")
        signature = self._hmac_sha256(k_signing, string_to_sign).hex()

        # 构造Authorization头
        authorization = "HMAC-SHA256 Credential={}, SignedHeaders={}, Signature={}".format(
            self.account_info.ak + "/" + credential_scope,
            signed_headers_str,
            signature,
        )

        headers["Authorization"] = authorization

        # 构造完整URL
        base_url = f"https://{self.host}/"
        full_url = f"{base_url}?{self._norm_query(query_params)}" if query_params else base_url

        return {"method": method, "url": full_url, "headers": headers, "body": body}
