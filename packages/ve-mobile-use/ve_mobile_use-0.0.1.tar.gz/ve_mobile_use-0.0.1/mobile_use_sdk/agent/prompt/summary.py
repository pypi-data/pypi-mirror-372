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

# Summarize our conversation up to this point. The summary should be a concise yet comprehensive overview of all key topics, questions, answers, and important details discussed. This summary will replace the current chat history to conserve tokens, so it must capture everything essential to understand the context and continue our conversation effectively as if no information was lost.
summary_system_prompt = """总结我们到目前为止的对话。摘要应该是对所有关键主题、问题、答案和讨论的重要细节的简洁而全面的概述。这个摘要将替换当前的聊天历史记录以节省tokens，因此它必须捕获所有必要信息，以便理解上下文并有效地继续我们的对话，就像没有丢失任何信息一样。\n\n下面是已经对话后的信息，请根据系统提示词的指示帮我总结一下我们干了什么:\n\n**注意：请直接处理下面的对话历史，不需要额外的解释。**"""
