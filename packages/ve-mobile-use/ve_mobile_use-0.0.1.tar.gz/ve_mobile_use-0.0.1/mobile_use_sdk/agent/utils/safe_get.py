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


def safe_get(obj, path, default=None):
    """Args:
        obj: 要访问的对象
        path: 访问路径，如 'args.0.0.value.request_user'
        default: 默认值.

    Returns:
        获取到的值或默认值
    """
    try:
        keys = path.split(".")
        result = obj
        for key in keys:
            if key.isdigit():
                # 处理数组索引
                result = result[int(key)]
            elif hasattr(result, key):
                # 处理对象属性
                result = getattr(result, key)
            elif isinstance(result, dict) and key in result:
                # 处理字典键
                result = result[key]
            else:
                return default
        return result
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return default
