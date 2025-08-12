# AI日记 API 文档

## 概述

AI日记提供完整的 RESTful API 接口，覆盖日记条目管理、AI分析、配置管理、用户认证、MCP 记忆管理、Notion集成、系统运维等能力。本文档与当前实现保持一致，列出可用端点与真实返回结构。

## 基础信息

- 基础URL: `http://localhost:5000/api`
- 认证方式: 基于 Session 的认证
- 数据格式: JSON（除文件上传外）
- 字符编码: UTF-8
- 时间基准: 默认使用北京时间 (UTC+8)

## 认证接口 (Auth)

### 登录
```
POST /auth/login
```

请求体:
```json
{ "password": "1234" }
```

响应:
```json
{ "success": true, "message": "登录成功" }
```

说明:
- 首次无密码时会自动创建默认密码 `1234`（使用安全哈希存储）。

### 登出
```
POST /auth/logout
```

响应:
```json
{ "success": true, "message": "登出成功" }
```

### 检查认证状态
```
GET /auth/check
```

响应:
```json
{ "authenticated": true }
```

### 修改密码
```
POST /auth/change-password
```

请求体:
```json
{ "current_password": "1234", "new_password": "5678" }
```

字段:
- `current_password`: 当系统已设置过密码时必须提供；首次设置可省略。
- `new_password`: 仅允许 1–4 位数字。

响应:
```json
{ "success": true, "message": "密码修改成功" }
```

## 日记接口 (Diary)

### 创建日记条目
```
POST /diary/entries
```

请求体 (multipart/form-data):
- `text_content`: 文字内容（可选）
- `image`: 图片文件（可选）

响应:
```json
{
  "success": true,
  "message": "日记条目创建成功",
  "entry": { "id": 1, "text_content": "...", "image_path": "uploads/xxx.jpg", "ai_analysis": "AI理解中...", "is_daily_summary": false, "timestamp": "...", "created_at": "..." }
}
```

### 获取日记条目列表
```
GET /diary/entries?page=1&per_page=20&date=2025-07-30&view=history
```

查询参数:
- `page`: 页码（默认 1）
- `per_page`: 每页条目数（默认 20）
- `date`: 按日期过滤（YYYY-MM-DD）
- `view`: 视图模式；未设或非`history`为时间线视图（排除每日总结），`history` 包含每日总结

响应:
```json
{
  "success": true,
  "entries": [ ... ],
  "pagination": { "page": 1, "per_page": 20, "total": 2, "pages": 1, "has_next": false, "has_prev": false }
}
```

### 获取单个日记条目
```
GET /diary/entries/{entry_id}
```

响应:
```json
{ "success": true, "entry": { ... } }
```

### 更新日记条目（仅文本）
```
PUT /diary/entries/{entry_id}
```

请求体:
```json
{ "text_content": "新的内容" }
```

响应:
```json
{ "success": true, "message": "日记条目更新成功", "entry": { ... } }
```

### 删除日记条目
```
DELETE /diary/entries/{entry_id}
```

响应:
```json
{ "success": true, "message": "日记条目删除成功" }
```

### 手动生成每日总结
系统会在每天北京时间 00:00 自动生成前一天的总结。此接口用于按日期手动生成或重新生成。
```
POST /diary/generate-daily-summary
```

请求体:
```json
{ "date": "2025-08-03" }
```

响应:
```json
{ "success": true, "message": "每日总结生成成功", "summary": "总结文本内容" }
```

说明:
- 必须提供 `date`（YYYY-MM-DD）。生成成功后会保存到数据库，并写入对应的每日总结条目。
- 执行行为：如该日已有总结，会先删除后重建（只保留一条最新总结）。
- 推送同步：生成成功后会触发 Telegram 推送与 Notion 同步（若已启用且配置完整）。

### 获取AI分析状态（单条）
```
GET /diary/entries/{entry_id}/analysis-status
```

响应:
```json
{ "success": true, "entry_id": 1, "ai_analysis": "...", "is_analyzing": false }
```

### 获取今日所有条目AI分析状态
```
GET /diary/entries/today/analysis-status
```

响应:
```json
{ "success": true, "entries": [ { "id": 1, "ai_analysis": "...", "is_analyzing": false, "timestamp": "..." } ] }
```

## MCP 接口 (Servers & Memories)

### 服务器列表
```
GET /mcp/servers
```

响应:
```json
{ "servers": [ { "id": 1, "name": "usermcp", "builtin": true, "enabled": true, "status": "running", ... } ] }
```

### 创建服务器
```
POST /mcp/servers
```

请求体:
```json
{ "name": "my-mcp-server", "command": "python", "args": ["-m","my_pkg"], "env": {"API_KEY":"xxx"}, "enabled": true }
```

响应:
```json
{ "message": "服务器配置创建成功", "server": { ... } }
```

### 更新服务器
```
PUT /mcp/servers/{server_id}
```

响应:
```json
{ "message": "服务器配置更新成功", "server": { ... } }
```

### 删除服务器
```
DELETE /mcp/servers/{server_id}
```

响应:
```json
{ "message": "服务器配置删除成功" }
```

### 启动/停止服务器
```
POST /mcp/servers/{server_id}/toggle
```

响应（示例）:
```json
{ "message": "服务器 usermcp 启动成功" }
```

### 获取用户记忆列表
```
GET /mcp/memories?type=preference&page=1&per_page=20&search=关键字
```

响应:
```json
{ "memories": [ ... ], "total": 1, "pages": 1, "current_page": 1 }
```

注：当前版本未提供公开的记忆创建/更新API；记忆主要由AI自动提取写入。

### 获取记忆统计
```
GET /mcp/memories/stats
```

响应:
```json
{ "stats": { "total_count": 25, "type_stats": [ ... ], "recent_memories": [ ... ] } }
```

### 删除单条记忆
```
DELETE /mcp/memories/{memory_id}
```

响应:
```json
{ "message": "记忆删除成功" }
```

### 批量删除记忆
```
DELETE /mcp/memories/batch
```

请求体:
```json
{ "memory_ids": [1,2,3] }
```

响应:
```json
{ "message": "成功删除 3 条记忆", "deleted_count": 3 }
```

### 清空所有记忆
```
DELETE /mcp/memories/clear
```

响应:
```json
{ "message": "成功清空 25 条记忆", "deleted_count": 25 }
```

### 获取MCP执行日志
```
GET /mcp/logs?page=1&per_page=50
```

响应:
```json
{ "logs": [ { "id": 1, "server_name": "usermcp", "tool_name": "usermcp_query_user_profile", "user_id": 1, "input_data": { ... }, "output_data": { ... }, "execution_time": 0.01, "status": "success", "error_message": null, "created_at": "..." } ], "total": 1, "pages": 1, "current_page": 1 }
```

## 管理接口 (Admin)

### 测试AI连接
```
POST /admin/test-ai
```

### 测试Telegram连接
```
POST /admin/test-telegram
```

### 手动生成指定日期总结
```
POST /admin/generate-summary
```

### 重新加载服务配置
```
POST /admin/reload-services
```

### 系统状态
```
GET /admin/system-status
```

响应:
```json
{ "success": true, "status": { "ai_configured": false, "telegram_configured": false, "scheduler_running": true, "timestamp": "2025-08-11T10:00:00" } }
```

## 错误处理

常见HTTP状态码：
- 200 成功 / 201 创建成功 / 204 删除成功
- 400 请求参数错误 / 401 未认证 / 404 资源不存在 / 500 服务器内部错误

返回结构说明：不同模块的返回结构略有差异（例如 MCP 列表接口无统一 `success` 字段），本文档已按当前实现示例化展示。

## 版本信息

- API版本: v1.1.1
- 最后更新: 2025-08-11
- 维护者: Manus AI
- 变更摘要: 修正文档与实现差异；更新手动总结接口；补充MCP删除/清空/日志接口；新增Admin接口说明。
    {
      "id": 1,
      "ai_analysis": "用户在享受美好的天气",
      "is_analyzing": false,
      "timestamp": "2025-07-30T16:45:00"
    }
  ]
}
```

### 获取每日汇总
```
GET /diary/summaries?date=2025-07-30
```

**响应**:
```json
{
  "success": true,
  "summaries": [
    {
      "id": 1,
      "date": "2025-07-30",
      "summary": "今天是美好的一天...",
      "created_at": "2025-07-30T23:59:00"
    }
  ]
}
```

## MCP接口 (Model Context Protocol)

MCP功能为AI提供长期记忆能力，支持用户偏好学习和个性化分析。

### 获取MCP服务器列表
```
GET /mcp/servers
```

**响应**:
```json
{
  "success": true,
  "servers": [
    {
      "id": 1,
      "name": "usermcp",
      "command": "builtin",
      "args": [],
      "env": {},
      "enabled": true,
      "builtin": true,
      "created_at": "2025-08-06T12:00:00",
      "updated_at": "2025-08-06T12:00:00"
    }
  ]
}
```

### 创建MCP服务器
```
POST /mcp/servers
```

**请求体**:
```json
{
  "name": "my-mcp-server",
  "command": "python",
  "args": ["-m", "my_mcp_package"],
  "env": {
    "API_KEY": "your-api-key"
  },
  "enabled": true
}
```

**响应**:
```json
{
  "success": true,
  "message": "MCP服务器创建成功",
  "server": {
    "id": 2,
    "name": "my-mcp-server",
    "command": "python",
    "args": ["-m", "my_mcp_package"],
    "env": {
      "API_KEY": "your-api-key"
    },
    "enabled": true,
    "builtin": false,
    "created_at": "2025-08-06T12:30:00",
    "updated_at": "2025-08-06T12:30:00"
  }
}
```

### 更新MCP服务器
```
PUT /mcp/servers/{server_id}
```

**请求体**:
```json
{
  "name": "updated-server-name",
  "enabled": false
}
```

**响应**:
```json
{
  "success": true,
  "message": "MCP服务器更新成功",
  "server": {
    "id": 2,
    "name": "updated-server-name",
    "enabled": false
  }
}
```

### 删除MCP服务器
```
DELETE /mcp/servers/{server_id}
```

**响应**:
```json
{
  "success": true,
  "message": "MCP服务器删除成功"
}
```

### 获取用户记忆列表
```
GET /mcp/memories?memory_type=preference&page=1&per_page=20
```

**查询参数**:
- `memory_type`: 记忆类型 (可选值: preference, habit, fact, emotion, experience)
- `page`: 页码 (默认: 1)
- `per_page`: 每页条目数 (默认: 20)

**响应**:
```json
{
  "success": true,
  "memories": [
    {
      "id": 1,
      "memory_type": "preference",
      "key": "food_preference",
      "value": "喜欢冬阴功汤，偏爱酸辣口味",
      "confidence": 0.95,
      "source": "ai_analysis",
      "tags": ["泰式料理", "汤类", "酸辣"],
      "created_at": "2025-08-06T10:30:00",
      "updated_at": "2025-08-06T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

### 创建用户记忆
```
POST /mcp/memories
```

**请求体**:
```json
{
  "memory_type": "preference",
  "key": "exercise_preference",
  "value": "喜欢晨跑，偏好户外运动",
  "confidence": 0.9,
  "tags": ["运动", "户外", "晨跑"]
}
```

**响应**:
```json
{
  "success": true,
  "message": "用户记忆创建成功",
  "memory": {
    "id": 2,
    "memory_type": "preference",
    "key": "exercise_preference",
    "value": "喜欢晨跑，偏好户外运动",
    "confidence": 0.9,
    "source": "manual",
    "tags": ["运动", "户外", "晨跑"],
    "created_at": "2025-08-06T11:00:00",
    "updated_at": "2025-08-06T11:00:00"
  }
}
```

### 更新用户记忆
```
PUT /mcp/memories/{memory_id}
```

**请求体**:
```json
{
  "value": "更新后的记忆内容",
  "confidence": 0.95,
  "tags": ["新标签1", "新标签2"]
}
```

**响应**:
```json
{
  "success": true,
  "message": "用户记忆更新成功",
  "memory": {
    "id": 2,
    "value": "更新后的记忆内容",
    "confidence": 0.95,
    "tags": ["新标签1", "新标签2"]
  }
}
```

### 删除用户记忆
```
DELETE /mcp/memories/{memory_id}
```

**响应**:
```json
{
  "success": true,
  "message": "用户记忆删除成功"
}
```

### 获取记忆统计
```
GET /mcp/memories/stats
```

**响应**:
```json
{
  "success": true,
  "stats": {
    "total_count": 25,
    "type_stats": [
      {
        "type": "preference",
        "count": 10
      },
      {
        "type": "habit",
        "count": 8
      },
      {
        "type": "fact",
        "count": 4
      },
      {
        "type": "emotion",
        "count": 2
      },
      {
        "type": "experience",
        "count": 1
      }
    ],
    "recent_memories": [
      {
        "id": 25,
        "memory_type": "preference",
        "key": "music_preference",
        "value": "喜欢听轻音乐，有助于放松心情",
        "created_at": "2025-08-06T10:30:00"
      }
    ]
  }
}
```

### 获取MCP执行日志
```
GET /mcp/logs?page=1&per_page=50
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页条目数 (默认: 50)

**响应**:
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "server_name": "usermcp",
      "tool_name": "query_user_profile",
      "user_id": 1,
      "input_data": {
        "query": "食物偏好"
      },
      "output_data": {
        "user_id": 1,
        "query": "食物偏好",
        "memories": [
          {
            "type": "preference",
            "key": "food_preference",
            "value": "喜欢冬阴功汤"
          }
        ]
      },
      "execution_time": 0.045,
      "status": "success",
      "error_message": null,
      "created_at": "2025-08-06T10:15:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 1,
    "pages": 1
  }
}
```

## 配置接口 (Config)

### 获取所有配置
```
GET /configs
```

**响应**:
```json
{
  "success": true,
  "configs": [
    {
      "id": 1,
      "key": "ai_api_url",
      "value": "https://api.openai.com/v1",
      "description": "AI API地址"
    }
  ]
}
```

### 获取指定配置
```
GET /configs/{key}
```

**响应**:
```json
{
  "success": true,
  "config": {
    "id": 1,
    "key": "ai_api_url",
    "value": "https://api.openai.com/v1",
    "description": "AI API地址"
  }
}
```

### 批量创建或更新配置
```
POST /configs
```

**请求体**:
```json
[
  {
    "key": "ai_api_url",
    "value": "https://api.openai.com/v1"
  },
  {
    "key": "ai_api_key",
    "value": "sk-..."
  }
]
```

**响应**:
```json
{
  "success": true,
  "message": "配置已成功保存",
  "configs": [...]
}
```

### 删除配置
```
DELETE /configs/{key}
```

**响应**:
```json
{
  "success": true,
  "message": "配置删除成功"
}
```

### 初始化默认配置
```
POST /configs/init-defaults
```

**响应**:
```json
{
  "success": true,
  "message": "成功初始化 10 个默认配置"
}
```

## Notion 集成接口

### 一键自动配置 Notion
```
POST /notion/auto-setup
```

**请求体**:
```json
{
  "token": "secret_xxxxxxxxxxxxx"
}
```

**响应**:
```json
{
  "success": true,
  "message": "自动配置成功",
  "page_title": "日记",
  "database_id": "12345678-1234-1234-1234-123456789abc",
  "setup_completed": true
}
```

**功能说明**:
- 验证 Notion Integration Token 有效性
- 自动搜索或创建"日记"页面
- 在页面下自动创建标准数据库结构
- 自动配置字段映射和选项
- 保存配置并启用同步功能

### 获取 Notion 配置状态
```
GET /notion/setup-status
```

**响应**:
```json
{
  "success": true,
  "configured": true,
  "has_token": true,
  "has_database": true,
  "enabled": true,
  "page_title": "日记",
  "database_name": "日记数据库"
}
```

### 测试 Notion 连接
```
GET /notion/test
```

**响应**:
```json
{
  "success": true,
  "message": "连接成功，用户: John Doe"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "API Token未配置"
}
```

### 字段映射与行为

同步每日总结时写入以下字段：
- Name（title）= 日记 YYYY年MM月DD日
- Date（date）= 当日日期（date-only）
- Content（rich_text）= 总结全文
- Mood（select）= 基于关键词识别
- Tags（multi_select）= 基于关键词提取，最多3个
- Word Count（number）= 正文字数
- Created By（select）= AI自动生成

说明：
- 不再写入“Summary/摘要”字段；若旧数据库有该字段，将不会更新。
- 查重策略：在配置的 database_id 中按 Date 精确查询，如存在则更新第一条，否则创建新页面；不会自动清理重复页面。
- 自动配置：每次调用会在目标页面下新建数据库并切换配置指向该库；如需复用旧库，请在配置中手动设置其 database_id。

## 管理接口 (Admin)

### 测试AI连接
```
POST /admin/test-ai
```

**请求体**:
```json
{
  "text": "测试文本"
}
```

**响应**:
```json
{
  "success": true,
  "message": "AI测试成功",
  "result": "这是AI的分析结果"
}
```

### 测试Telegram连接
```
POST /admin/test-telegram
```

**响应**:
```json
{
  "success": true,
  "message": "测试消息发送成功"
}
```

### 手动生成日记汇总
```
POST /admin/generate-summary
```

**请求体**:
```json
{
  "date": "2025-07-30"
}
```

**响应**:
```json
{
  "success": true,
  "message": "汇总生成成功"
}
```

### 重新加载服务配置
```
POST /admin/reload-services
```

**响应**:
```json
{
  "success": true,
  "message": "服务配置重新加载成功"
}
```

### 获取系统状态
```
GET /admin/system-status
```

**响应**:
```json
{
  "success": true,
  "status": {
    "ai_configured": true,
    "telegram_configured": false,
    "scheduler_running": true,
    "timestamp": "2025-07-30T16:45:00"
  }
}
```

## 用户接口 (User)

### 获取所有用户
```
GET /users
```

**响应**:
```json
[
  {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com"
  }
]
```

### 创建用户
```
POST /users
```

**请求体**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com"
}
```

**响应**:
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com"
}
```
字段说明：

- `username`：用户名，不能为空，且不能与已有用户重复。
- `email`：邮箱地址，不能为空，且不能与已有用户重复。

当用户名或邮箱为空，或者已存在同名或同邮箱的用户时，服务器将返回400错误。

### 获取指定用户
```
GET /users/{user_id}
```

**响应**:
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com"
}
```

### 更新用户
```
PUT /users/{user_id}
```

**请求体**:
```json
{
  "username": "updateduser",
  "email": "updated@example.com"
}
```

**响应**:
```json
{
  "id": 1,
  "username": "updateduser",
  "email": "updated@example.com"
}
```

### 删除用户
```
DELETE /users/{user_id}
```

**响应**: 204 No Content

## 错误处理

所有API接口在发生错误时都会返回统一的错误格式：

```json
{
  "success": false,
  "message": "错误描述"
}
```

常见HTTP状态码：
- `200`: 成功
- `201`: 创建成功
- `204`: 删除成功
- `400`: 请求参数错误
- `401`: 未认证
- `404`: 资源不存在
- `500`: 服务器内部错误

## 配置项说明

| 配置键 | 描述 | 默认值 |
|--------|------|--------|
| `ai_api_url` | AI API地址 | `https://api.openai.com/v1` |
| `ai_api_key` | AI API密钥 | 空 |
| `ai_model` | AI模型名称 | `gpt-3.5-turbo` |
| `ai_prompt_template` | AI分析提示词模板（已集成MCP记忆功能） | 默认中文提示词 |
| `ai_summary_prompt` | AI每日汇总提示词（已集成MCP记忆功能） | 默认中文汇总提示词 |
| `telegram_bot_token` | Telegram机器人Token | 空 |
| `telegram_chat_id` | Telegram聊天ID | 空 |
| `telegram_enabled` | 是否启用Telegram推送 | `false` |

## MCP记忆类型说明

| 记忆类型 | 描述 | 示例 |
|---------|------|------|
| `preference` | 用户偏好，包括食物、活动、音乐等喜好 | "喜欢冬阴功汤，偏爱酸辣口味" |
| `habit` | 生活习惯和行为模式 | "习惯早上7点起床，喜欢晨跑" |
| `fact` | 关于用户的客观事实信息 | "在某某公司工作，居住在北京" |
| `emotion` | 情感模式和触发点 | "工作压力大时容易焦虑，听音乐可以放松" |
| `experience` | 重要经历和特殊事件 | "去年夏天的欧洲旅行让人印象深刻" |

## 使用示例

### 创建一个包含文字和图片的日记条目

```javascript
const formData = new FormData();
formData.append('text_content', '今天去了公园');
formData.append('image', imageFile);

fetch('/api/diary/entries', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('日记创建成功:', data);
});
```

### 实时检查AI分析状态

```javascript
function checkAnalysisStatus() {
  fetch('/api/diary/entries/today/analysis-status')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        data.entries.forEach(entry => {
          if (entry.is_analyzing) {
            console.log('条目', entry.id, '正在分析中...');
          } else {
            console.log('条目', entry.id, '分析完成:', entry.ai_analysis);
          }
        });
      }
    });
}

### MCP记忆管理示例

```javascript
// 获取用户的所有偏好记忆
fetch('/api/mcp/memories?memory_type=preference')
  .then(response => response.json())
  .then(data => {
    console.log('用户偏好记忆:', data.memories);
  });

// 手动添加一个新的记忆
const newMemory = {
  memory_type: 'habit',
  key: 'sleep_schedule',
  value: '通常在晚上11点睡觉，早上7点起床',
  confidence: 0.8,
  tags: ['睡眠', '作息', '健康']
};

fetch('/api/mcp/memories', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newMemory)
})
.then(response => response.json())
.then(data => {
  console.log('记忆添加成功:', data);
});

// 查看记忆统计信息
fetch('/api/mcp/memories/stats')
  .then(response => response.json())
  .then(data => {
    console.log('总记忆数:', data.stats.total_count);
    console.log('各类型统计:', data.stats.type_stats);
  });
```

### MCP工具执行监控

```javascript
// 查看MCP工具的执行日志
fetch('/api/mcp/logs?page=1&per_page=10')
  .then(response => response.json())
  .then(data => {
    data.logs.forEach(log => {
      console.log(`${log.created_at}: ${log.tool_name} - ${log.status}`);
      if (log.status === 'error') {
        console.error('错误信息:', log.error_message);
      }
    });
  });
```

## 版本信息

- **API版本**: v1.1.2
- **最后更新**: 2025-08-12
- **维护者**: Manus AI
- **变更摘要**: 修正 Notion 接口文档以匹配实现；手动生成总结说明新增推送与同步；去除“Summary/摘要”字段描述；说明调度按北京时间运行。
