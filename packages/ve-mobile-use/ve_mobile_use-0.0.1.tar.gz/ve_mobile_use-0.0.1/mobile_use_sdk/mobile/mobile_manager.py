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

from mobile_use_sdk.config.config import TosInfo

from .impl.cloud_phone import CloudPhone


class PhoneManager:
    """手机管理器，统一管理鉴权信息和手机实例创建."""

    def __init__(
        self,
        ak: str,
        sk: str,
        account_id: str,
        tos_info: TosInfo | None = None,
    ) -> None:
        """初始化手机管理器.

        Args:
            ak: 访问密钥 ID
            sk: 访问密钥
            tos_info: TOS 配置信息，如果为 None 则使用默认配置
        """
        self.ak = ak
        self.sk = sk
        self.account_id = account_id
        self.tos_info = tos_info or TosInfo()

    async def create_cloud_phone(
        self,
        pod_id: str,
        product_id: str,
    ) -> CloudPhone:
        """创建并初始化云手机实例.

        Args:
            pod_id: Pod ID
            product_id: 产品 ID

        Returns:
            已初始化的 CloudPhone 实例
        """
        # 创建 CloudPhone 实例
        cloud_phone = CloudPhone(
            ak=self.ak,
            sk=self.sk,
            account_id=self.account_id,
            tos_info=self.tos_info,
        )

        # 初始化云手机客户端
        await cloud_phone.initialize(
            pod_id=pod_id,
            product_id=product_id,
        )

        return cloud_phone
