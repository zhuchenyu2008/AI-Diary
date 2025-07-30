# AI日记应用部署指南

本文档详细说明了如何在不同环境中部署AI日记应用。

## 系统要求

### 最低要求
- **操作系统**: Linux、Windows、macOS
- **Python版本**: 3.8 或更高版本
- **内存**: 512MB RAM
- **存储空间**: 100MB 可用空间
- **网络**: 互联网连接（用于AI API调用）

### 推荐配置
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **Python版本**: 3.9 或更高版本
- **内存**: 1GB RAM 或更多
- **存储空间**: 1GB 可用空间
- **网络**: 稳定的互联网连接

## 开发环境部署

### 1. 环境准备

#### 安装Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS (使用Homebrew)
brew install python3

# Windows
# 从 https://python.org 下载并安装Python
```

#### 克隆项目
```bash
git clone https://github.com/zhuchenyu2008/AI-Diary.git
cd AI-Diary
```

### 2. 虚拟环境设置

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 如果遇到权限问题
pip install --user -r requirements.txt
```

### 4. 数据库初始化

```bash
# 创建数据库目录
mkdir -p src/database

# 启动应用（首次启动会自动创建数据库）
python src/main.py
```

### 5. 访问应用

打开浏览器访问：http://localhost:5000

默认登录密码：`1234`

## 生产环境部署

### 方式一：使用Gunicorn部署

#### 1. 安装Gunicorn
```bash
pip install gunicorn
```

#### 2. 创建Gunicorn配置文件
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. 启动应用
```bash
gunicorn -c gunicorn.conf.py src.main:app
```

### 方式二：使用Nginx + Gunicorn

#### 1. 安装Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置Nginx
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

#### 3. 启用站点
```bash
sudo ln -s /etc/nginx/sites-available/ai-diary /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式三：使用Docker部署

#### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据库目录
RUN mkdir -p src/database

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# 启动应用
CMD ["python", "src/main.py"]
```

#### 2. 构建镜像
```bash
docker build -t ai-diary .
```

#### 3. 运行容器
```bash
# 基本运行
docker run -p 5000:5000 ai-diary

# 持久化数据
docker run -p 5000:5000 -v $(pwd)/data:/app/src/database ai-diary

# 后台运行
docker run -d -p 5000:5000 --name ai-diary-app ai-diary
```

#### 4. 使用Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-diary:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/src/database
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ai-diary
    restart: unless-stopped
```

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 进程管理

### 使用Systemd（推荐）

#### 1. 创建服务文件
```ini
# /etc/systemd/system/ai-diary.service
[Unit]
Description=AI Diary Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/AI-Diary
Environment=PATH=/path/to/AI-Diary/venv/bin
ExecStart=/path/to/AI-Diary/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 启用服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-diary
sudo systemctl start ai-diary
sudo systemctl status ai-diary
```

### 使用Supervisor

#### 1. 安装Supervisor
```bash
sudo apt install supervisor
```

#### 2. 创建配置文件
```ini
# /etc/supervisor/conf.d/ai-diary.conf
[program:ai-diary]
command=/path/to/AI-Diary/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
directory=/path/to/AI-Diary
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-diary.log
```

#### 3. 启动服务
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-diary
```

## SSL/HTTPS配置

### 使用Let's Encrypt

#### 1. 安装Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

#### 2. 获取SSL证书
```bash
sudo certbot --nginx -d your-domain.com
```

#### 3. 自动续期
```bash
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 环境变量配置

创建 `.env` 文件：
```bash
# .env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///src/database/app.db

# AI配置
AI_API_URL=https://api.openai.com/v1
AI_API_KEY=your-openai-api-key
AI_MODEL=gpt-3.5-turbo

# Telegram配置
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

## 数据库管理

### 备份数据库
```bash
# 创建备份
cp src/database/app.db backups/app_$(date +%Y%m%d_%H%M%S).db

# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DB_FILE="/path/to/AI-Diary/src/database/app.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/app_$DATE.db

# 保留最近30天的备份
find $BACKUP_DIR -name "app_*.db" -mtime +30 -delete
```

### 恢复数据库
```bash
# 停止应用
sudo systemctl stop ai-diary

# 恢复数据库
cp backups/app_20250730_120000.db src/database/app.db

# 启动应用
sudo systemctl start ai-diary
```

## 监控和日志

### 日志配置
```python
# 在main.py中添加日志配置
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

### 性能监控
```bash
# 安装htop监控系统资源
sudo apt install htop

# 监控应用进程
ps aux | grep gunicorn

# 查看端口使用情况
sudo netstat -tlnp | grep :5000
```

## 安全配置

### 防火墙设置
```bash
# Ubuntu UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 应用安全
1. 修改默认密码
2. 使用强密码
3. 定期更新依赖包
4. 限制文件上传大小
5. 配置CORS策略

## 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查找占用端口的进程
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>
```

#### 2. 权限问题
```bash
# 修改文件权限
sudo chown -R www-data:www-data /path/to/AI-Diary
sudo chmod -R 755 /path/to/AI-Diary
```

#### 3. 数据库锁定
```bash
# 检查数据库文件权限
ls -la src/database/app.db

# 修复权限
sudo chown www-data:www-data src/database/app.db
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h

# 添加交换空间
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 日志分析
```bash
# 查看应用日志
tail -f logs/ai-diary.log

# 查看系统日志
sudo journalctl -u ai-diary -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 性能优化

### 应用优化
1. 使用数据库连接池
2. 启用静态文件缓存
3. 压缩响应内容
4. 优化数据库查询

### 服务器优化
1. 调整Gunicorn worker数量
2. 配置Nginx缓存
3. 使用CDN加速静态资源
4. 启用gzip压缩

## 更新和维护

### 应用更新
```bash
# 备份当前版本
cp -r AI-Diary AI-Diary-backup

# 拉取最新代码
cd AI-Diary
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart ai-diary
```

### 定期维护
1. 定期备份数据库
2. 清理日志文件
3. 更新系统包
4. 监控磁盘空间
5. 检查SSL证书有效期

## 扩展部署

### 负载均衡
```nginx
upstream ai_diary_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://ai_diary_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 数据库分离
考虑使用PostgreSQL或MySQL替代SQLite：

```python
# 配置PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/ai_diary"
```

### 容器编排
使用Kubernetes进行大规模部署：

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-diary
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-diary
  template:
    metadata:
      labels:
        app: ai-diary
    spec:
      containers:
      - name: ai-diary
        image: ai-diary:latest
        ports:
        - containerPort: 5000
```

---

本部署指南涵盖了从开发环境到生产环境的完整部署流程。根据实际需求选择合适的部署方式，并注意安全和性能优化。

