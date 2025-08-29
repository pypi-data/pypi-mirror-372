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

from volcenginesdkarkruntime import Ark

from mobile_use_sdk.config.config import LLMConfig


class ArkTokenCounter:
    max_input_context = 96000  # 128k
    context_ratio = 0.80

    def __init__(self, llm_config: LLMConfig) -> None:
        self.api_key = llm_config.api_key
        self.model_name = llm_config.model

    def count_image_token(self, image_size: tuple[int, int], detail_mode: str = "low") -> int:
        """计算图片token用量.

        Args:
            image_numbers: 图片数量
            image_size: 图片尺寸 (width, height)
            detail_mode: 细节模式 "high" 或 "low"

        Returns:
            图片总token数

        token 用量说明:
        - token 用量，根据图片宽高像素计算可得。图片转化 token 的公式为：
          min(图片宽 * 图片高÷784, 单图 token 限制)
          detail:high模式下，单图 token 限制升至 5120 token。
          detail:low模式下，单图 token 限制 1312 token。
        """
        width, height = image_size

        # 基础token计算：图片宽 * 图片高 / 784
        base_tokens_per_image = (width * height) // 784

        token_limit_per_image = 5120 if detail_mode.lower() == "high" else 1312

        # 计算单图实际token数：min(基础token, token限制)
        return min(base_tokens_per_image, token_limit_per_image)

    async def count_text_token(self, text: str) -> int:
        # 计算文本token
        ark_client = Ark(api_key=self.api_key)
        resp = ark_client.tokenization.create(
            model=self.model_name,
            text=[text],
        )
        text_tokens = 0
        if len(resp.data) > 0 and isinstance(resp.data[0].total_tokens, int | float):
            text_tokens = resp.data[0].total_tokens
        else:
            text_tokens = len(text)

        return text_tokens

    async def is_token_exceed(
        self,
        text: str,
        image_numbers: int = 0,
        image_size: tuple[int, int] | None = None,
        detail_mode: str = "low",
    ) -> bool:
        """检查总token数是否超出限制（文本 + 图片）.

        Args:
            text: 文本内容
            image_numbers: 图片数量（可选）
            image_size: 图片尺寸 (width, height)（可选）
            detail_mode: 图片细节模式 "high" 或 "low"

        Returns:
            是否超出token限制
        """
        image_tokens = 0
        if image_numbers > 0:
            image_tokens = image_numbers * self.count_image_token(image_size=image_size, detail_mode=detail_mode)
        preview_token = len(text) + image_tokens

        limited_token = self.max_input_context * self.context_ratio

        # 如果预先的 token 没有超出，说明没超过
        if preview_token < limited_token:
            return False

        # 若果超过了
        text_token = await self.count_text_token(text)
        return (text_token + image_tokens) > limited_token
