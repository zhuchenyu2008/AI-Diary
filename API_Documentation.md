# 杯子日记 API 文档

## 概述

杯子日记是一个新型的日记应用，支持用户通过文字和图片记录生活，使用AI大模型理解内容并自动生成日记摘要。本文档详细描述了所有可用的API接口。

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: 简单密码认证（1-4位数字）
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证接口

### 登录

**POST** `/auth/login`

用户登录接口，验证密码并返回认证状态。

#### 请求参数

```json
{
  "password": "1234"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| password | string | 是 | 1-4位数字密码 |

#### 响应示例

**成功响应 (200)**
```json
{
  "success": true,
  "message": "登录成功"
}
```

**失败响应 (401)**
```json
{
  "success": false,
  "message": "密码错误"
}
```

### 登出

**POST** `/auth/logout`

用户登出接口。

#### 响应示例

```json
{
  "success": true,
  "message": "登出成功"
}
```

### 修改密码

**POST** `/auth/change-password`

修改登录密码。

#### 请求参数

```json
{
  "old_password": "1234",
  "new_password": "5678"
}
```

#### 响应示例

**成功响应 (200)**
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

## 日记接口

### 创建日记条目

**POST** `/diary/entries`

创建新的日记条目，支持文字和图片。

#### 请求参数

**Content-Type**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text_content | string | 否 | 文字内容 |
| image | file | 否 | 图片文件 |

#### 响应示例

**成功响应 (201)**
```json
{
  "success": true,
  "message": "日记条目创建成功",
  "data": {
    "id": 1,
    "timestamp": "2025-07-28T12:30:00.000Z",
    "text_content": "今天天气很好",
    "image_path": "/uploads/images/20250728_123000_abc123.jpg",
    "ai_analysis": "用户今天心情愉快，在享受美好的天气",
    "created_at": "2025-07-28T12:30:00.000Z"
  }
}
```

### 获取今日日记条目

**GET** `/diary/entries/today`

获取今天的所有日记条目。

#### 响应示例

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timestamp": "2025-07-28T12:30:00.000Z",
      "text_content": "今天天气很好",
      "image_path": "/uploads/images/20250728_123000_abc123.jpg",
      "ai_analysis": "用户今天心情愉快，在享受美好的天气",
      "created_at": "2025-07-28T12:30:00.000Z"
    }
  ]
}
```

### 获取历史日记条目

**GET** `/diary/entries`

获取历史日记条目，支持分页和日期筛选。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页条数，默认20 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 1,
        "timestamp": "2025-07-28T12:30:00.000Z",
        "text_content": "今天天气很好",
        "image_path": "/uploads/images/20250728_123000_abc123.jpg",
        "ai_analysis": "用户今天心情愉快，在享受美好的天气",
        "created_at": "2025-07-28T12:30:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 删除日记条目

**DELETE** `/diary/entries/{id}`

删除指定的日记条目。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 日记条目ID |

#### 响应示例

```json
{
  "success": true,
  "message": "日记条目删除成功"
}
```

### 获取每日汇总

**GET** `/diary/summaries`

获取每日汇总列表。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页条数，默认10 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "summaries": [
      {
        "id": 1,
        "date": "2025-07-28",
        "summary_content": "今天是美好的一天，用户心情愉快...",
        "entry_count": 3,
        "created_at": "2025-07-29T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 获取指定日期汇总

**GET** `/diary/summaries/{date}`

获取指定日期的汇总。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 是 | 日期 (YYYY-MM-DD) |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "id": 1,
    "date": "2025-07-28",
    "summary_content": "今天是美好的一天，用户心情愉快...",
    "entry_count": 3,
    "created_at": "2025-07-29T00:00:00.000Z"
  }
}
```

### 手动生成汇总

**POST** `/diary/summaries/generate`

手动触发生成指定日期的汇总。

#### 请求参数

```json
{
  "date": "2025-07-28"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "汇总生成成功",
  "data": {
    "id": 1,
    "date": "2025-07-28",
    "summary_content": "今天是美好的一天，用户心情愉快...",
    "entry_count": 3,
    "created_at": "2025-07-29T00:00:00.000Z"
  }
}
```

## 配置接口

### 获取配置列表

**GET** `/configs`

获取所有系统配置。

#### 响应示例

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "key": "ai_api_url",
      "value": "https://api.openai.com/v1",
      "description": "AI API地址",
      "created_at": "2025-07-28T00:00:00.000Z",
      "updated_at": "2025-07-28T00:00:00.000Z"
    }
  ]
}
```

### 更新配置

**PUT** `/configs/{key}`

更新指定配置项。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | 配置键名 |

#### 请求参数

```json
{
  "value": "新的配置值"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "配置更新成功",
  "data": {
    "id": 1,
    "key": "ai_api_url",
    "value": "新的配置值",
    "description": "AI API地址",
    "created_at": "2025-07-28T00:00:00.000Z",
    "updated_at": "2025-07-28T12:30:00.000Z"
  }
}
```

## 管理接口

### 测试Telegram连接

**POST** `/admin/test-telegram`

测试Telegram机器人连接。

#### 响应示例

**成功响应**
```json
{
  "success": true,
  "message": "连接成功！机器人：MyDiaryBot"
}
```

**失败响应**
```json
{
  "success": false,
  "message": "Bot Token未配置"
}
```

### 发送测试消息

**POST** `/admin/send-test-message`

发送测试消息到Telegram。

#### 请求参数

```json
{
  "message": "这是一条测试消息"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "测试消息发送成功"
}
```

### 获取系统状态

**GET** `/admin/status`

获取系统运行状态。

#### 响应示例

```json
{
  "success": true,
  "data": {
    "total_entries": 150,
    "total_summaries": 30,
    "today_entries": 5,
    "ai_configured": true,
    "telegram_configured": true,
    "telegram_enabled": false
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 配置项说明

### AI配置

| 配置键 | 说明 | 默认值 |
|--------|------|--------|
| ai_api_url | AI API地址 | https://api.openai.com/v1 |
| ai_api_key | AI API密钥 | 空 |
| ai_model | AI模型名称 | gpt-3.5-turbo |
| ai_prompt_template | AI分析提示词模板 | 请分析这个用户的日记内容... |
| ai_summary_prompt | AI每日汇总提示词 | 请根据用户今天的所有日记条目... |

### Telegram配置

| 配置键 | 说明 | 默认值 |
|--------|------|--------|
| telegram_bot_token | Telegram机器人Token | 空 |
| telegram_chat_id | Telegram聊天ID | 空 |
| telegram_enabled | 是否启用Telegram推送 | false |

## 使用示例

### JavaScript示例

```javascript
// 登录
const login = async (password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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

// 获取今日条目
const getTodayEntries = async () => {
  const response = await fetch('/api/diary/entries/today');
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
def create_entry(text_content=None, image_path=None):
    data = {}
    files = {}
    
    if text_content:
        data['text_content'] = text_content
    if image_path:
        files['image'] = open(image_path, 'rb')
    
    response = requests.post('http://localhost:5000/api/diary/entries',
                           data=data, files=files)
    return response.json()

# 获取历史条目
def get_entries(page=1, per_page=20):
    params = {'page': page, 'per_page': per_page}
    response = requests.get('http://localhost:5000/api/diary/entries',
                          params=params)
    return response.json()
```

## 注意事项

1. **文件上传**: 图片文件大小限制为16MB，支持常见图片格式（JPG、PNG、GIF等）
2. **认证状态**: 登录状态通过Session维护，浏览器会自动处理
3. **时区**: 所有时间戳均为UTC时间，前端需要根据用户时区进行转换
4. **AI功能**: 需要配置有效的AI API密钥才能使用AI分析功能
5. **Telegram推送**: 需要配置Bot Token和Chat ID才能使用推送功能
6. **定时任务**: 每日汇总在每天00:00自动生成
7. **数据备份**: 建议定期备份SQLite数据库文件

## 更新日志

### v1.0.0 (2025-07-28)
- 初始版本发布
- 支持基础的日记记录功能
- 集成AI分析功能
- 支持Telegram推送
- 实现每日自动汇总

