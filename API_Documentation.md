# AI日记 API 文档

## 概述

AI日记是一个智能日记应用，提供了完整的RESTful API接口，支持日记条目管理、AI分析、配置管理、用户认证等功能。

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: Session-based authentication
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证接口 (Auth)

### 登录
```
POST /auth/login
```

**请求体**:
```json
{
  "password": "1234"
}
```

**响应**:
```json
{
  "success": true,
  "message": "登录成功"
}
```

### 登出
```
POST /auth/logout
```

**响应**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 检查认证状态
```
GET /auth/check
```

**响应**:
```json
{
  "authenticated": true
}
```

### 修改密码
```
POST /auth/change-password
```

**请求体**:
```json
{
  "current_password": "1234",
  "new_password": "5678"
}
```

**响应**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

## 日记接口 (Diary)

### 创建日记条目
```
POST /diary/entries
```

**请求体** (multipart/form-data):
- `text_content`: 文字内容 (可选)
- `image`: 图片文件 (可选)

**响应**:
```json
{
  "success": true,
  "message": "日记条目创建成功",
  "entry": {
    "id": 1,
    "text_content": "今天天气很好",
    "image_path": "uploads/image.jpg",
    "ai_analysis": "AI理解中...",
    "timestamp": "2025-07-30T16:45:00"
  }
}
```

### 获取日记条目列表
```
GET /diary/entries?page=1&per_page=20&date=2025-07-30
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页条目数 (默认: 20)
- `date`: 日期过滤 (格式: YYYY-MM-DD)

**响应**:
```json
{
  "success": true,
  "entries": [
    {
      "id": 1,
      "text_content": "今天天气很好",
      "image_path": "uploads/image.jpg",
      "ai_analysis": "用户在享受美好的天气",
      "timestamp": "2025-07-30T16:45:00"
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

### 获取单个日记条目
```
GET /diary/entries/{entry_id}
```

**响应**:
```json
{
  "success": true,
  "entry": {
    "id": 1,
    "text_content": "今天天气很好",
    "image_path": "uploads/image.jpg",
    "ai_analysis": "用户在享受美好的天气",
    "timestamp": "2025-07-30T16:45:00"
  }
}
```

### 删除日记条目
```
DELETE /diary/entries/{entry_id}
```

**响应**:
```json
{
  "success": true,
  "message": "日记条目删除成功"
}
```

### 获取AI分析状态
```
GET /diary/entries/{entry_id}/analysis-status
```

**响应**:
```json
{
  "success": true,
  "entry_id": 1,
  "ai_analysis": "用户在享受美好的天气",
  "is_analyzing": false
}
```

### 获取今日所有条目的AI分析状态
```
GET /diary/entries/today/analysis-status
```

**响应**:
```json
{
  "success": true,
  "entries": [
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
  "message": "成功初始化 8 个默认配置"
}
```

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
| `ai_prompt_template` | AI分析提示词模板 | 默认中文提示词 |
| `ai_summary_prompt` | AI每日汇总提示词 | 默认中文汇总提示词 |
| `telegram_bot_token` | Telegram机器人Token | 空 |
| `telegram_chat_id` | Telegram聊天ID | 空 |
| `telegram_enabled` | 是否启用Telegram推送 | `false` |

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

// 每2秒检查一次
setInterval(checkAnalysisStatus, 2000);
```

## 版本信息

- **API版本**: v1.0
- **最后更新**: 2025-07-30
- **维护者**: Manus AI

