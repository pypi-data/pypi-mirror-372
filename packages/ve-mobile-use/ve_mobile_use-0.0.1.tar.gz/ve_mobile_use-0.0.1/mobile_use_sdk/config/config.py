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
import os

import dotenv
from pydantic import BaseModel

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    model: str = os.getenv("ARK_MODEL_ID")
    api_key: str = os.getenv("ARK_API_KEY")
    base_url: str = os.getenv("ARK_BASE_URL")


class AgentConfig(BaseModel):
    additional_system_prompt: str = ""
    step_interval: float = 0.8
    max_steps: int = 256
    use_base64_screenshot: bool = False


class VolcEngineAuth(BaseModel):
    ak: str = os.getenv("ACEP_AK")
    sk: str = os.getenv("ACEP_SK")
    account_id: str = os.getenv("ACEP_ACCOUNT_ID")


class TosInfo(BaseModel):
    ak: str = os.getenv("TOS_AK", os.getenv("ACEP_AK"))
    sk: str = os.getenv("TOS_SK", os.getenv("ACEP_SK"))
    bucket: str = os.getenv("TOS_BUCKET")
    region: str = os.getenv("TOS_REGION")
    endpoint: str = os.getenv("TOS_ENDPOINT")
