# AI日记应用开发文档

## 项目概述

AI日记应用是一个智能的日记记录系统，支持多模态输入（文字、图片），通过AI自动分析内容并生成生动的日记。

## 技术架构

### 后端技术栈
- **FastAPI**: 现代化的Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **MySQL**: 主数据库
- **Redis**: 缓存和任务队列
- **Celery**: 异步任务处理
- **JWT**: 用户认证

### AI服务
- **OpenAI GPT**: 文本生成和分析
- **Claude**: 备选AI服务
- **Google Gemini**: 备选AI服务

### 存储服务
- **AWS S3**: 云存储
- **阿里云OSS**: 备选存储
- **本地存储**: 开发环境

## 项目结构

```
ai-diary-app/
├── app/                    # 主应用目录
│   ├── api/               # API路由
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py      # 认证相关
│   │           ├── health.py    # 健康检查
│   │           ├── moments.py   # 瞬间管理
│   │           └── diaries.py   # 日记管理
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库连接
│   │   └── security.py    # 安全相关
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── moment.py      # 瞬间模型
│   │   └── diary.py       # 日记模型
│   ├── services/          # 业务服务
│   │   ├── ai_service.py      # AI服务
│   │   ├── storage_service.py # 存储服务
│   │   └── diary_service.py   # 日记服务
│   └── main.py            # 应用入口
├── scripts/               # 脚本文件
│   ├── init_db.py         # 数据库初始化
│   ├── create_admin.py    # 创建管理员
│   └── init.sql           # MySQL初始化SQL
├── tests/                 # 测试文件
├── docs/                  # 文档
├── docker-compose.yml     # Docker配置
├── Dockerfile             # Docker镜像
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 核心功能

### 1. 用户管理
- 用户注册（邮箱可选）
- 用户登录（用户名+密码）
- JWT令牌认证

### 2. 瞬间记录
- 支持文字输入
- 支持图片上传
- 支持图文结合
- AI自动分析内容

### 3. 日记生成
- 自动生成每日日记
- 手动触发生成
- AI内容优化

### 4. 存储管理
- 图片压缩和优化
- 多种存储后端支持
- 预签名URL生成

## API接口

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录

### 瞬间接口
- `POST /api/v1/moments` - 创建瞬间
- `GET /api/v1/moments` - 获取瞬间列表

### 日记接口
- `GET /api/v1/diaries` - 获取日记列表
- `GET /api/v1/diaries/recent` - 获取最近日记
- `POST /api/v1/diaries/summarize-today` - 生成今日日记

### 健康检查
- `GET /api/v1/health` - 系统健康检查

## 数据库设计

### 用户表 (users)
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(128) UNIQUE NULL,  -- 可选字段
  password_hash VARCHAR(255) NOT NULL,
  telegram_chat_id VARCHAR(50) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 瞬间表 (moments)
```sql
CREATE TABLE moments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  image_url VARCHAR(1024) NULL,
  user_text TEXT NULL,
  ai_description_origin TEXT NULL,
  ai_description_final TEXT NULL,
  image_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 日记表 (daily_diaries)
```sql
CREATE TABLE daily_diaries (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  diary_date DATE NOT NULL,
  content_origin TEXT NOT NULL,
  content_final TEXT NULL,
  pushed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_date (user_id, diary_date),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 环境配置

### 必需的环境变量
```bash
# 应用配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_diary_db

# AI服务配置（至少配置一个）
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_VISION_MODEL=gpt-4-vision-preview
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_VISION_MODEL=claude-3-vision-20240229
GOOGLE_API_KEY=your-google-api-key
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
GOOGLE_MODEL=gemini-pro
GOOGLE_VISION_MODEL=gemini-pro-vision

# 存储配置（至少配置一个）
STORAGE_TYPE=s3  # s3, oss, local
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-bucket-name
# 阿里云OSS，可选
OSS_ACCESS_KEY_ID=your-oss-access-key
OSS_ACCESS_KEY_SECRET=your-oss-secret-key
OSS_ENDPOINT=your-oss-endpoint
OSS_BUCKET_NAME=your-oss-bucket
```

## 开发指南

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd ai-diary-app

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库设置
```bash
# 创建.env文件
cp env.example .env
# 编辑.env文件，配置数据库连接

# 初始化数据库
python scripts/init_db.py
```

### 3. 启动应用
```bash
# 开发模式
python start.py

# 或者使用uvicorn
uvicorn app.main:app --reload
```

### 4. 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py
```

## 部署指南

### Docker部署
```bash
# 使用Docker Compose
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 生产环境配置
1. 修改环境变量为生产配置
2. 配置SSL证书
3. 设置数据库备份
4. 配置监控和日志
5. 设置防火墙规则

## 安全考虑

### 1. 认证安全
- 使用强密码策略
- JWT令牌定期轮换
- 密码加密存储（bcrypt）

### 2. 数据安全
- 数据库连接加密
- 敏感信息环境变量存储
- 文件上传类型和大小限制

### 3. API安全
- CORS配置
- 请求频率限制
- 输入验证和清理

## 监控和日志

### 1. 应用监控
- 健康检查端点
- 性能指标收集
- 错误追踪

### 2. 日志管理
- 结构化日志
- 日志级别配置
- 日志轮转

## 扩展功能

### 1. 计划功能
- Telegram推送集成
- 邮件通知
- 移动端应用
- 数据导出

### 2. 技术改进
- WebSocket实时通信
- 图片识别优化
- 多语言支持
- 缓存优化

## 故障排除

### 常见问题
1. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串
   - 确认网络连接

2. **AI服务调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 查看错误日志

3. **文件上传失败**
   - 检查存储服务配置
   - 验证文件大小限制
   - 确认文件类型

### 调试技巧
- 启用调试模式
- 查看详细日志
- 使用API文档测试
- 检查数据库状态

## 贡献指南

### 代码规范
- 使用Black格式化代码
- 遵循PEP 8规范
- 添加类型注解
- 编写单元测试

### 提交规范
- 使用清晰的提交信息
- 一个提交一个功能
- 包含测试用例
- 更新相关文档

## 许可证

MIT License 