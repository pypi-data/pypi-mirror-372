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

from typing import Any

from pydantic import BaseModel

from mobile_use_sdk.config.config import VolcEngineAuth
from mobile_use_sdk.volcengine_openapi.volcengine_openapi_signer import (
    VolcEngineOpenAPISigner,
)


class Credentials(BaseModel):
    ak: str
    sk: str


class ServiceInfo(BaseModel):
    credentials: Credentials


class ACEP_Signer:
    """ACEP管理器，提供STS token生成功能."""

    def __init__(self, ak: str, sk: str, account_id: str) -> None:
        """初始化管理器."""
        self.account_info = VolcEngineAuth(ak=ak, sk=sk, account_id=account_id)
        self.signer = VolcEngineOpenAPISigner(account_info=self.account_info)

    def generate_mobile_use_mcp_token(self, expire_duration: int = 1000 * 60 * 30) -> dict[str, Any]:
        """生成Mobile Use MCP token（这个方法需要使用volcengine SDK）."""
        from volcengine.base.Service import Service

        volc_client = Service(
            service_info=ServiceInfo(
                credentials=Credentials(
                    ak=self.account_info.access_key_id,
                    sk=self.account_info.secret_key,
                )
            ),
            api_info={},
        )
        volc_client.set_region("cn-north-1")
        volc_client.set_host("open.volcengineapi.com")
        volc_client.set_scheme("https")

        volc_policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["ACEP:*", "iPaaS:*", "tos:*"],
                    "Resource": ["*"],
                }
            ]
        }
        volc_user_token = volc_client.sign_sts2(policy=volc_policy, expire=expire_duration)
        return {
            "AccessKeyID": volc_user_token.access_key_id,
            "SecretAccessKey": volc_user_token.secret_access_key,
            "SessionToken": volc_user_token.session_token,
            "CurrentTime": volc_user_token.current_time,
            "ExpiredTime": volc_user_token.expired_time,
        }

    def _compute_auth_token(self, sts_token: dict[str, Any]) -> str:
        """计算认证token."""
        import base64
        import json

        auth_dict = {
            "AccessKeyId": self.account_info.access_key_id,
            "SecretAccessKey": self.account_info.secret_key,
            "CurrentTime": sts_token["CurrentTime"],
            "ExpiredTime": sts_token["ExpiredTime"],
            "SessionToken": "",
        }
        auth_bytes = json.dumps(auth_dict).encode("utf-8")
        return base64.b64encode(auth_bytes).decode("utf-8")

    def generate_remote_mcp_auth(self) -> str:
        """生成远程MCP认证."""
        mcp_sts_token = self.generate_mobile_use_mcp_token()
        return self._compute_auth_token(mcp_sts_token)
