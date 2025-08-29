# Mobile Use SDK

云手机智能操作SDK，基于AI大模型实现云手机的自动化操作和智能交互。

[Mobile Use SDK 使用指南](https://www.volcengine.com/docs/6394/1783697)

## 🚀 产品概述

[Mobile Use 解决方案介绍文档](https://www.volcengine.com/docs/6394/1583515)

**Mobile Use** 是基于 **火山引擎云手机** 与 **豆包视觉大模型** 能力，通过自然语言指令完成面向移动端场景自动化任务的 AI Agent 解决方案。


目前，Mobile Use 已正式上线火山引擎 [函数服务 veFaaS 应用广场](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/market)，可点击跳转在线体验 Mobile Use Agent Demo；同时，如果您想要开发一款属于您自己的 Mobile Use Agent 应用，可以通过 [一键部署](https://console.volcengine.com/vefaas/region:vefaas+cn-beijing/application/create)，快速完成服务部署搭建，开启您将 Mobile Use Agent 集成在您业务流中的开发之旅。

## 🚀 项目介绍

Mobile Use SDK 是一个强大的云手机自动化操作框架，通过AIMobileUse实现对云手机的自动化控制。该SDK集成了大语言模型、图状态机和MCP工具协议，为移动应用测试、自动化操作和智能交互提供完整解决方案。

### 核心特性

- **🤖 Mobile Use**: 基于 LangGraph 的 ReAct Agent，支持复杂多步骤任务自动执行
- **📱 云手机操作**: 完整的云手机控制能力（启动应用、截图、点击、滑动、输入等）
- **🔄 流式交互**: 实时流式响应，支持用户中断和交互反馈
- **📊 结构化输出**: 支持自定义Pydantic模型的结构化数据输出
- **🔧 MCP工具集成**: 支持Model Context Protocol工具生态扩展
- **⚡ 连接池管理**: 自动管理MCP和云手机连接，提高性能和稳定性


### 使用方法

详见[Mobile Use SDK 使用指南](https://www.volcengine.com/docs/6394/1783697)
