# AI日记应用 - 快速启动指南

## 🚀 5分钟快速启动

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- MySQL 8.0+
- Redis (可选，用于生产环境)

### 2. 克隆项目

```bash
git clone <repository-url>
cd ai-diary-app
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，可自定义 AI 接口地址和模型，至少配置以下必需项：
```

**必需配置项：**
```bash
# 应用密钥（请生成强密钥）
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
JWT_SECRET_KEY=your-jwt-secret-key-here-make-it-long-and-random

# 数据库连接
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_diary_db

# AI服务（至少配置一个）
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_VISION_MODEL=gpt-4-vision-preview
# 或者配置Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_VISION_MODEL=claude-3-vision-20240229
# 或者配置Google Gemini
GOOGLE_API_KEY=your-google-api-key
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
GOOGLE_MODEL=gemini-pro
GOOGLE_VISION_MODEL=gemini-pro-vision

# 存储配置（开发环境可以使用本地存储）
STORAGE_TYPE=local
```

### 5. 初始化数据库

```bash
# 运行数据库初始化脚本
python scripts/init_db.py
```

### 6. 启动应用

```bash
# 使用启动脚本
python start.py

# 或者直接使用uvicorn
uvicorn app.main:app --reload
```

### 7. 访问应用

- **API文档**: http://localhost:8000/docs
- **应用首页**: http://localhost:8000

## 📝 快速测试

### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
  }'
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 3. 创建瞬间（需要登录令牌）

```bash
# 替换 YOUR_TOKEN 为登录返回的access_token
curl -X POST "http://localhost:8000/api/v1/moments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text=今天天气真好，心情愉快！"
```

## 🐳 Docker快速启动

如果您更喜欢使用Docker：

### 1. 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 2. 访问应用

- **API文档**: http://localhost:8000/docs
- **应用首页**: http://localhost:8000

## 🔧 常见问题

### Q: 数据库连接失败
**A:** 检查MySQL服务是否启动，确认连接字符串正确

### Q: AI服务调用失败
**A:** 检查API密钥配置，确认网络连接正常

### Q: 文件上传失败
**A:** 检查存储配置，确认文件大小和类型符合要求

### Q: 端口被占用
**A:** 修改.env文件中的端口配置，或停止占用端口的服务

## 📚 下一步

1. **阅读完整文档**: 查看 `docs/development.md`
2. **配置生产环境**: 参考部署指南
3. **添加更多功能**: 查看扩展功能列表
4. **参与开发**: 查看贡献指南

## 🆘 获取帮助

- **文档**: 查看 `docs/` 目录
- **API文档**: 访问 http://localhost:8000/docs
- **问题反馈**: 提交Issue到项目仓库

---

**注意**: 首次启动时，请确保所有必需的环境变量都已正确配置。如果遇到问题，请查看日志输出获取详细错误信息。 