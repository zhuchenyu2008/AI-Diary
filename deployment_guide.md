# AI日记 v2.0 部署指南

本指南详细说明了如何在不同环境中部署AI日记应用，包括开发环境、测试环境和生产环境。

## 📋 系统要求

### 基础要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+), macOS, Windows 10+
- **Python**: 3.8 或更高版本
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 1GB 可用空间
- **网络**: 需要访问AI API服务（如OpenAI）

### 可选依赖（MCP功能）
- **uv**: Python包管理器，用于MCP服务器管理
- **Node.js**: 某些MCP服务器可能需要
- **Docker**: 容器化部署（可选）

## 🚀 快速部署

### 1. 基础部署

#### 步骤1：获取代码
```bash
# 克隆项目
git clone https://github.com/zhuchenyu2008/AI-Diary.git
cd AI-Diary

# 或者解压提供的项目包
tar -xzf AI-Diary-v2.0-upgraded.tar.gz
cd AI-Diary
```

#### 步骤2：创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

#### 步骤3：安装Python依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 验证安装
python -c "import flask; print('Flask安装成功')"
```

#### 步骤4：初始化数据库
```bash
# 创建数据库目录
mkdir -p src/database

# 初始化数据库（如果有初始化脚本）
python src/init_db.py
```

#### 步骤5：启动应用
```bash
# 开发模式启动
python src/main.py

# 应用将在 http://localhost:5000 启动
```

### 2. MCP功能部署

如果需要使用MCP（Model Context Protocol）功能，需要额外安装相关依赖。

#### 安装uv包管理器
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证安装
uv --version
```

#### 安装MCP服务器包
```bash
# 安装常用MCP服务器
uvx install mcp-server-time
uvx install mcp-server-weather

# 验证安装
uvx mcp-server-time --help
```

#### 配置MCP服务器
1. 启动应用后访问设置页面
2. 点击"管理 MCP 服务器"
3. 添加内置服务器模板或自定义配置

## 🔧 详细配置

### 环境变量配置

创建 `.env` 文件（可选）：
```bash
# AI服务配置
AI_API_BASE=https://api.openai.com/v1
AI_API_KEY=your-openai-api-key
AI_MODEL=gpt-3.5-turbo

# 应用配置
SECRET_KEY=your-secret-key-here
DEBUG=False
PORT=5000

# 数据库配置
DATABASE_URL=sqlite:///src/database/app.db

# MCP配置
MCP_ENABLED=true
MCP_TIMEOUT=30

# Telegram配置（可选）
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 应用配置

#### 首次启动配置
1. **设置登录密码**
   - 默认密码：`1234`
   - 首次登录后建议修改

2. **配置AI服务**
   - API地址：`https://api.openai.com/v1`
   - API密钥：需要有效的OpenAI API密钥
   - 模型：`gpt-3.5-turbo` 或其他支持的模型

3. **配置Telegram推送（可选）**
   - 创建Telegram机器人获取Token
   - 获取Chat ID
   - 在设置中启用推送功能

## 🏭 生产环境部署

### 方式1：使用Gunicorn + Nginx

#### 安装Gunicorn
```bash
pip install gunicorn
```

#### 创建Gunicorn配置文件
```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 启动Gunicorn
```bash
# 启动应用
gunicorn -c gunicorn.conf.py src.main:app

# 或者直接指定参数
gunicorn -w 4 -b 127.0.0.1:5000 src.main:app
```

#### 配置Nginx
```nginx
# /etc/nginx/sites-available/ai-diary
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/AI-Diary/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 启用Nginx配置
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/ai-diary /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 方式2：使用Docker部署

#### 创建Dockerfile
```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装uv（用于MCP功能）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p src/database data/uploads

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=src.main:app
ENV FLASK_ENV=production

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
```

#### 创建docker-compose.yml
```yaml
version: '3.8'

services:
  ai-diary:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./src/database:/app/src/database
    environment:
      - AI_API_KEY=${AI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-diary
    restart: unless-stopped
```

#### 构建和运行
```bash
# 构建镜像
docker build -t ai-diary:v2.0 .

# 运行容器
docker run -d \
  --name ai-diary \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e AI_API_KEY=your-api-key \
  ai-diary:v2.0

# 或使用docker-compose
docker-compose up -d
```

### 方式3：使用Systemd服务

#### 创建服务文件
```ini
# /etc/systemd/system/ai-diary.service
[Unit]
Description=AI Diary Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-diary
Environment=PATH=/opt/ai-diary/venv/bin
ExecStart=/opt/ai-diary/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启用和启动服务
```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable ai-diary

# 启动服务
sudo systemctl start ai-diary

# 查看状态
sudo systemctl status ai-diary
```

## 🔒 安全配置

### SSL/TLS配置

#### 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

#### Nginx SSL配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 防火墙配置
```bash
# 使用ufw配置防火墙
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 应用安全
1. **修改默认密码**：首次登录后立即修改
2. **API密钥安全**：使用环境变量存储，不要硬编码
3. **定期备份**：备份数据库和配置文件
4. **监控日志**：定期检查应用和系统日志

## 📊 监控和维护

### 日志配置

#### 应用日志
```python
# 在main.py中配置日志
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/ai-diary.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### Nginx日志
```nginx
# 在nginx配置中
access_log /var/log/nginx/ai-diary-access.log;
error_log /var/log/nginx/ai-diary-error.log;
```

### 性能监控

#### 使用htop监控系统资源
```bash
sudo apt install htop
htop
```

#### 监控应用进程
```bash
# 查看Gunicorn进程
ps aux | grep gunicorn

# 查看端口占用
sudo netstat -tlnp | grep :5000
```

### 备份策略

#### 数据库备份
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_FILE="/opt/ai-diary/src/database/app.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/app_$DATE.db

# 保留最近30天的备份
find $BACKUP_DIR -name "app_*.db" -mtime +30 -delete
```

#### 自动备份
```bash
# 添加到crontab
crontab -e
# 每天凌晨2点备份
0 2 * * * /opt/ai-diary/backup.sh
```

## 🔧 故障排除

### 常见问题

#### 1. 应用无法启动
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list | grep flask

# 检查端口占用
sudo lsof -i :5000

# 查看错误日志
tail -f logs/ai-diary.log
```

#### 2. AI功能不工作
- 检查API密钥是否正确
- 验证网络连接
- 查看API调用日志
- 确认API额度充足

#### 3. MCP服务器启动失败
```bash
# 检查uv安装
uv --version

# 手动测试MCP服务器
uvx mcp-server-time --help

# 查看MCP日志
tail -f logs/mcp.log
```

#### 4. 图片上传失败
- 检查上传目录权限
- 验证文件大小限制
- 确认浏览器权限设置

#### 5. 移动端显示异常
- 清除浏览器缓存
- 检查CSS文件加载
- 验证响应式设计

### 性能优化

#### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_diary_created_at ON diary_entries(created_at);
CREATE INDEX idx_diary_user_id ON diary_entries(user_id);
```

#### 2. 静态文件缓存
```nginx
location /static/ {
    alias /opt/ai-diary/src/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip on;
    gzip_types text/css application/javascript;
}
```

#### 3. 应用缓存
```python
# 使用Flask-Caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def get_daily_summary(date):
    # 缓存每日汇总
    pass
```

## 📈 扩展部署

### 负载均衡部署

#### 多实例部署
```bash
# 启动多个Gunicorn实例
gunicorn -w 4 -b 127.0.0.1:5001 src.main:app &
gunicorn -w 4 -b 127.0.0.1:5002 src.main:app &
gunicorn -w 4 -b 127.0.0.1:5003 src.main:app &
```

#### Nginx负载均衡配置
```nginx
upstream ai_diary_backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://ai_diary_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 数据库扩展

#### 使用PostgreSQL
```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE ai_diary;
CREATE USER ai_diary_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_diary TO ai_diary_user;
```

#### 修改配置
```python
# 在配置中使用PostgreSQL
DATABASE_URL = 'postgresql://ai_diary_user:your_password@localhost/ai_diary'
```

## 🔄 更新和升级

### 应用更新流程

#### 1. 备份当前版本
```bash
# 备份数据库
cp src/database/app.db backup/app_$(date +%Y%m%d).db

# 备份配置
cp -r src/static/config backup/config_$(date +%Y%m%d)
```

#### 2. 下载新版本
```bash
# 下载新版本
wget https://github.com/zhuchenyu2008/AI-Diary/archive/v2.1.tar.gz

# 解压到临时目录
tar -xzf v2.1.tar.gz -C /tmp/
```

#### 3. 更新应用
```bash
# 停止服务
sudo systemctl stop ai-diary

# 更新代码
rsync -av --exclude='src/database/' --exclude='data/' /tmp/AI-Diary-2.1/ /opt/ai-diary/

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 运行数据库迁移（如果有）
python src/migrate.py

# 重启服务
sudo systemctl start ai-diary
```

### 版本回滚

#### 快速回滚
```bash
# 停止服务
sudo systemctl stop ai-diary

# 恢复备份
cp backup/app_20250730.db src/database/app.db

# 切换到旧版本代码
git checkout v2.0

# 重启服务
sudo systemctl start ai-diary
```

## 📞 技术支持

### 获取帮助
- **GitHub Issues**: https://github.com/zhuchenyu2008/AI-Diary/issues
- **文档**: 查看项目README和API文档
- **社区**: 参与GitHub Discussions

### 报告问题
提交问题时请包含：
1. 详细的错误描述
2. 复现步骤
3. 系统环境信息
4. 相关日志文件

### 贡献代码
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

本部署指南涵盖了AI日记v2.0的完整部署流程。如有任何问题，请参考故障排除部分或联系技术支持。

