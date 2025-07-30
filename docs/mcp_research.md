# MCP (Model Context Protocol) 研究报告

## 概述

Model Context Protocol (MCP) 是一个开放标准，用于在AI应用程序和外部数据源之间建立安全的双向连接。它使AI模型能够实时访问外部工具和数据源。

## 核心架构

### 参与者

MCP采用客户端-服务器架构，包含三个核心组件：

1. **MCP Host（主机）**: AI应用程序，协调和管理一个或多个MCP客户端
2. **MCP Client（客户端）**: 维护与MCP服务器连接的组件，为主机获取上下文
3. **MCP Server（服务器）**: 向MCP客户端提供上下文的程序

### 层次结构

MCP包含两个层次：

1. **数据层**: 定义基于JSON-RPC 2.0的协议，用于客户端-服务器通信
2. **传输层**: 定义通信机制和通道，支持数据交换

### 核心原语（Primitives）

MCP定义了三种核心原语，服务器可以暴露：

1. **Tools（工具）**: AI应用程序可以调用的可执行函数
2. **Resources（资源）**: 为AI应用程序提供上下文信息的数据源
3. **Prompts（提示）**: 帮助构建与语言模型交互的可重用模板

## 传输机制

MCP支持两种传输机制：

1. **Stdio传输**: 使用标准输入/输出流进行本地进程通信
2. **Streamable HTTP传输**: 使用HTTP POST进行远程服务器通信

## 在AI日记系统中的应用

### 可能的MCP服务器功能

1. **时间服务器**: 提供当前时间、时区信息、日期计算等
2. **位置服务器**: 提供用户位置信息（需要权限）
3. **天气服务器**: 根据位置提供天气信息
4. **日历服务器**: 提供日程安排信息
5. **系统信息服务器**: 提供设备信息、电池状态等

### 实现方案

1. 创建内置MCP客户端
2. 实现多个MCP服务器
3. 在前端提供可视化配置界面
4. 集成到AI分析流程中


## MCP服务器概念详解

### 核心构建块

MCP服务器通过三个构建块提供功能：

1. **Tools（工具）**
   - 用途：AI执行操作
   - 控制方：模型控制
   - 示例：搜索航班、发送消息、创建日历事件
   - 协议操作：
     - `tools/list`: 发现可用工具
     - `tools/call`: 执行特定工具

2. **Resources（资源）**
   - 用途：提供上下文数据
   - 控制方：应用程序控制
   - 示例：文档、日历、邮件、天气数据
   - 协议操作：
     - `resources/list`: 列出可用资源
     - `resources/templates/list`: 发现资源模板
     - `resources/read`: 检索资源内容
     - `resources/subscribe`: 监控资源变化

3. **Prompts（提示）**
   - 用途：交互模板
   - 控制方：用户控制
   - 示例："计划假期"、"总结我的会议"、"起草邮件"

### 资源模板

资源模板支持动态资源访问，使用URI模板：
- `weather://forecast/{city}/{date}` - 天气预报
- `travel://flights/{origin}/{destination}` - 航班搜索

## MCP客户端概念详解

### 核心客户端功能

1. **Sampling（采样）**
   - 允许服务器通过客户端请求语言模型完成
   - 启用代理行为，同时保持安全性和用户控制
   - 包含人工审核环节

2. **Roots（根目录）**
   - 定义服务器操作的文件系统边界
   - 使用file://URI方案
   - 帮助服务器理解项目边界

3. **Elicitation（引出）**
   - 允许服务器从用户请求额外信息
   - 支持交互式工作流

## 远程MCP服务器

### 优势
- 可访问性：无需在每个设备上安装配置
- 适合Web应用程序
- 支持服务器端处理和认证

### 连接流程
1. 导航到连接器设置
2. 添加自定义连接器
3. 完成身份验证
4. 访问资源和提示
5. 配置工具权限

## 在AI日记系统中的具体实现方案

### 1. 时间服务器
- **Tools**: 
  - `getCurrentTime()`: 获取当前时间
  - `getTimezone()`: 获取时区信息
  - `calculateDuration()`: 计算时间间隔
- **Resources**:
  - `time://current`: 当前时间信息
  - `time://timezone/{zone}`: 特定时区信息

### 2. 位置服务器
- **Tools**:
  - `getCurrentLocation()`: 获取当前位置（需要权限）
  - `getLocationInfo()`: 获取位置详细信息
- **Resources**:
  - `location://current`: 当前位置
  - `location://history`: 位置历史

### 3. 天气服务器
- **Tools**:
  - `getWeather()`: 获取天气信息
  - `getWeatherForecast()`: 获取天气预报
- **Resources**:
  - `weather://current/{location}`: 当前天气
  - `weather://forecast/{location}/{days}`: 天气预报

### 4. 系统信息服务器
- **Tools**:
  - `getDeviceInfo()`: 获取设备信息
  - `getBatteryStatus()`: 获取电池状态
- **Resources**:
  - `system://device`: 设备信息
  - `system://battery`: 电池状态

