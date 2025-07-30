# AI日记系统 API 文档

## 概述

AI日记系统提供了一套完整的RESTful API，支持用户认证、日记管理、AI分析、配置管理等功能。

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: Session认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证相关 API

### 1. 用户登录

**接口**: `POST /api/auth/login`

**描述**: 用户登录系统

**请求参数**:
```json
{
  "password": "1234"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "密码错误"
}
```

### 2. 用户登出

**接口**: `POST /api/auth/logout`

**描述**: 用户登出系统

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 3. 检查认证状态

**接口**: `GET /api/auth/check`

**描述**: 检查当前用户的认证状态

**响应示例**:
```json
{
  "authenticated": true
}
```

### 4. 修改密码

**接口**: `POST /api/auth/change-password`

**描述**: 修改用户密码（需要认证）

**请求参数**:
```json
{
  "new_password": "5678"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

## 日记管理 API

### 1. 创建日记条目

**接口**: `POST /api/diary/entries`

**描述**: 创建新的日记条目（支持文字和图片）

**请求方式**: `multipart/form-data`

**请求参数**:
- `text_content` (可选): 文字内容
- `image` (可选): 图片文件

**响应示例**:
```json
{
  "success": true,
  "message": "日记条目创建成功",
  "entry": {
    "id": 1,
    "text_content": "今天天气很好",
    "image_path": "uploads/abc123.jpg",
    "ai_analysis": null,
    "timestamp": "2025-07-30T14:30:00"
  }
}
```

### 2. 获取日记条目列表

**接口**: `GET /api/diary/entries`

**描述**: 获取日记条目列表（支持分页和日期过滤）

**查询参数**:
- `page` (可选): 页码，默认为1
- `per_page` (可选): 每页条目数，默认为20
- `date` (可选): 日期过滤，格式为YYYY-MM-DD

**响应示例**:
```json
{
  "success": true,
  "entries": [
    {
      "id": 1,
      "text_content": "今天天气很好",
      "image_path": "uploads/abc123.jpg",
      "ai_analysis": "用户在享受美好的天气",
      "timestamp": "2025-07-30T14:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 3. 获取单个日记条目

**接口**: `GET /api/diary/entries/{entry_id}`

**描述**: 获取指定ID的日记条目

**响应示例**:
```json
{
  "success": true,
  "entry": {
    "id": 1,
    "text_content": "今天天气很好",
    "image_path": "uploads/abc123.jpg",
    "ai_analysis": "用户在享受美好的天气",
    "timestamp": "2025-07-30T14:30:00"
  }
}
```

### 4. 删除日记条目

**接口**: `DELETE /api/diary/entries/{entry_id}`

**描述**: 删除指定ID的日记条目

**响应示例**:
```json
{
  "success": true,
  "message": "日记条目删除成功"
}
```

### 5. 获取AI分析状态

**接口**: `GET /api/diary/entries/{entry_id}/analysis-status`

**描述**: 获取日记条目的AI分析状态

**响应示例**:
```json
{
  "success": true,
  "entry_id": 1,
  "has_analysis": true,
  "ai_analysis": "用户在享受美好的天气",
  "status": "completed"
}
```

### 6. 获取今日倒计时

**接口**: `GET /api/diary/today-countdown`

**描述**: 获取距离今日结束的倒计时

**响应示例**:
```json
{
  "success": true,
  "countdown": {
    "hours": 9,
    "minutes": 30,
    "seconds": 15,
    "total_seconds": 34215
  }
}
```

## 日记汇总 API

### 1. 获取汇总列表

**接口**: `GET /api/diary/summaries`

**描述**: 获取每日汇总列表

**查询参数**:
- `page` (可选): 页码，默认为1
- `per_page` (可选): 每页条目数，默认为30
- `days` (可选): 获取最近多少天的汇总，默认为365

**响应示例**:
```json
{
  "success": true,
  "summaries": [
    {
      "id": 1,
      "date": "2025-07-30",
      "summary": "今天是美好的一天...",
      "entry_count": 5,
      "created_at": "2025-07-31T00:05:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 30,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 2. 获取指定日期汇总

**接口**: `GET /api/diary/summaries/{date}`

**描述**: 获取指定日期的汇总（日期格式：YYYY-MM-DD）

**响应示例**:
```json
{
  "success": true,
  "summary": {
    "id": 1,
    "date": "2025-07-30",
    "summary": "今天是美好的一天...",
    "entry_count": 5,
    "created_at": "2025-07-31T00:05:00"
  }
}
```

## 配置管理 API

### 1. 获取所有配置

**接口**: `GET /api/configs`

**描述**: 获取系统所有配置项（需要认证）

**响应示例**:
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

### 2. 获取指定配置

**接口**: `GET /api/configs/{key}`

**描述**: 获取指定键的配置项

**响应示例**:
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

### 3. 批量更新配置

**接口**: `POST /api/configs`

**描述**: 批量创建或更新配置项

**请求参数**:
```json
[
  {
    "key": "ai_api_url",
    "value": "https://api.openai.com/v1"
  },
  {
    "key": "ai_api_key",
    "value": "sk-xxx"
  }
]
```

**响应示例**:
```json
{
  "success": true,
  "message": "配置已成功保存",
  "configs": [...]
}
```

### 4. 删除配置

**接口**: `DELETE /api/configs/{key}`

**描述**: 删除指定键的配置项

**响应示例**:
```json
{
  "success": true,
  "message": "配置删除成功"
}
```

### 5. 初始化默认配置

**接口**: `POST /api/configs/init-defaults`

**描述**: 初始化系统默认配置

**响应示例**:
```json
{
  "success": true,
  "message": "成功初始化 8 个默认配置"
}
```

## 管理员 API

### 1. 测试AI连接

**接口**: `POST /api/admin/test-ai`

**描述**: 测试AI服务连接状态

**请求参数**:
```json
{
  "text": "测试文本"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "AI测试成功",
  "result": "这是AI的分析结果"
}
```

### 2. 测试Telegram连接

**接口**: `POST /api/admin/test-telegram`

**描述**: 测试Telegram机器人连接状态

**响应示例**:
```json
{
  "success": true,
  "message": "测试消息发送成功"
}
```

### 3. 手动生成汇总

**接口**: `POST /api/admin/generate-summary`

**描述**: 手动生成指定日期的日记汇总

**请求参数**:
```json
{
  "date": "2025-07-30"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "汇总生成成功"
}
```

### 4. 重新加载服务配置

**接口**: `POST /api/admin/reload-services`

**描述**: 重新加载AI和Telegram服务配置

**响应示例**:
```json
{
  "success": true,
  "message": "服务配置重新加载成功"
}
```

### 5. 获取系统状态

**接口**: `GET /api/admin/system-status`

**描述**: 获取系统各服务的运行状态

**响应示例**:
```json
{
  "success": true,
  "status": {
    "ai_configured": true,
    "telegram_configured": false,
    "scheduler_running": true,
    "timestamp": "2025-07-30T14:30:00"
  }
}
```

## 错误处理

### 通用错误格式

所有API在发生错误时都会返回以下格式的响应：

```json
{
  "success": false,
  "message": "错误描述"
}
```

### 常见HTTP状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 数据模型

### DiaryEntry（日记条目）

```json
{
  "id": 1,
  "text_content": "文字内容",
  "image_path": "图片路径",
  "ai_analysis": "AI分析结果",
  "timestamp": "创建时间"
}
```

### DailySummary（每日汇总）

```json
{
  "id": 1,
  "date": "日期",
  "summary": "汇总内容",
  "entry_count": "条目数量",
  "created_at": "创建时间"
}
```

### Config（配置项）

```json
{
  "id": 1,
  "key": "配置键",
  "value": "配置值",
  "description": "配置描述"
}
```

## 使用示例

### JavaScript示例

```javascript
// 登录
const login = async (password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ password })
  });
  return await response.json();
};

// 创建日记条目
const createEntry = async (textContent, imageFile) => {
  const formData = new FormData();
  if (textContent) formData.append('text_content', textContent);
  if (imageFile) formData.append('image', imageFile);
  
  const response = await fetch('/api/diary/entries', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};

// 获取日记列表
const getEntries = async (date) => {
  const url = date ? `/api/diary/entries?date=${date}` : '/api/diary/entries';
  const response = await fetch(url);
  return await response.json();
};
```

### Python示例

```python
import requests

# 登录
def login(password):
    response = requests.post('http://localhost:5000/api/auth/login', 
                           json={'password': password})
    return response.json()

# 创建日记条目
def create_entry(text_content=None, image_file=None):
    files = {}
    data = {}
    
    if text_content:
        data['text_content'] = text_content
    if image_file:
        files['image'] = open(image_file, 'rb')
    
    response = requests.post('http://localhost:5000/api/diary/entries',
                           data=data, files=files)
    return response.json()

# 获取日记列表
def get_entries(date=None):
    params = {'date': date} if date else {}
    response = requests.get('http://localhost:5000/api/diary/entries',
                          params=params)
    return response.json()
```

## 注意事项

1. **认证**: 大部分API需要先通过 `/api/auth/login` 进行认证
2. **文件上传**: 图片上传最大支持16MB
3. **图片格式**: 支持 PNG、JPG、JPEG、GIF、WEBP 格式
4. **时区**: 所有时间戳都使用北京时间（UTC+8）
5. **分页**: 列表接口都支持分页，默认每页20条记录
6. **CORS**: API支持跨域请求

## 更新日志

- **v1.0.0** (2025-07-30): 初始版本发布
  - 基础认证功能
  - 日记CRUD操作
  - AI分析功能
  - 配置管理
  - 管理员功能

