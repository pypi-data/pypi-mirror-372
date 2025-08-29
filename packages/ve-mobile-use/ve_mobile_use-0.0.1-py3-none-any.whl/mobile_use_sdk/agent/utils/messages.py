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

import uuid

from langchain_core.messages import HumanMessage
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL

# def merge_human_message(a_human_message: HumanMessage, b_human_message: HumanMessage):
#     if not isinstance(a_human_message.content, list):
#         a_human_message.content = [a_human_message.content]
#     if not isinstance(b_human_message.content, list):
#         b_human_message.content = [b_human_message.content]
#     a_human_message.content.extend(b_human_message.content)
#     return a_human_message


def get_human_message(user_content: str, url: str | None = None) -> HumanMessage:
    #  UserPrompt
    user_message = ChatCompletionContentPartTextParam(text=user_content, type="text")
    screenshot_message = HumanMessage(role="user", content=[user_message], id=str(uuid.uuid4()))

    # 添加截图消息
    if url:
        snap_content = ChatCompletionContentPartImageParam(image_url=ImageURL(url=url), type="image_url")
        screenshot_message.content.append(snap_content)

    return screenshot_message
