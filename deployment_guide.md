# 杯子日记部署指南

本文档详细说明了如何在不同环境中部署杯子日记应用。

## 部署架构

杯子日记采用前后端分离的架构：
- **前端**: React应用，构建后的静态文件
- **后端**: Flask API服务器
- **数据库**: SQLite（轻量级，适合单用户）
- **文件存储**: 本地文件系统

## 环境要求

### 最低要求
- **操作系统**: Linux/Windows/macOS
- **Python**: 3.8+
- **Node.js**: 16+
- **内存**: 512MB+
- **存储**: 1GB+

### 推荐配置
- **操作系统**: Ubuntu 20.04+ / CentOS 8+
- **Python**: 3.9+
- **Node.js**: 18+
- **内存**: 2GB+
- **存储**: 10GB+

## 开发环境部署

### 1. 环境准备

```bash
# 安装Python和Node.js
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm

# macOS (使用Homebrew)
brew install python node
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd diary-app
```

### 3. 后端设置

```bash
cd diary_backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建必要目录
mkdir -p src/database src/uploads/images

# 启动开发服务器
python src/main.py
```

### 4. 前端设置

```bash
cd diary_frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问应用

- 前端开发服务器: http://localhost:3000
- 后端API服务器: http://localhost:5000
- 默认密码: `1234`

## 生产环境部署

### 方式一：传统部署

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install python3 python3-pip python3-venv nodejs npm nginx supervisor git -y

# 创建应用用户
sudo useradd -m -s /bin/bash diary
sudo usermod -aG sudo diary
```

#### 2. 应用部署

```bash
# 切换到应用用户
sudo su - diary

# 克隆项目
git clone <repository-url> /home/diary/diary-app
cd /home/diary/diary-app

# 后端设置
cd diary_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建必要目录
mkdir -p src/database src/uploads/images src/static

# 前端构建
cd ../diary_frontend
npm install
npm run build

# 复制构建文件到后端静态目录
cp -r dist/* ../diary_backend/src/static/
```

#### 3. Nginx配置

```bash
# 创建Nginx配置文件
sudo nano /etc/nginx/sites-available/diary-app
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 静态文件
    location /static/ {
        alias /home/diary/diary-app/diary_backend/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /uploads/ {
        alias /home/diary/diary-app/diary_backend/src/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API请求
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
        root /home/diary/diary-app/diary_backend/src/static;
        index index.html;
    }

    # 文件上传大小限制
    client_max_body_size 16M;
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/diary-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Supervisor配置

```bash
# 创建Supervisor配置
sudo nano /etc/supervisor/conf.d/diary-app.conf
```

```ini
[program:diary-app]
command=/home/diary/diary-app/diary_backend/venv/bin/python /home/diary/diary-app/diary_backend/src/main.py
directory=/home/diary/diary-app/diary_backend
user=diary
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/diary-app.log
environment=PYTHONPATH="/home/diary/diary-app/diary_backend"
```

```bash
# 重新加载Supervisor配置
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start diary-app
```

#### 5. SSL配置（可选）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 方式二：Docker部署

#### 1. 创建Dockerfile

```dockerfile
# diary_backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p src/database src/uploads/images src/static

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "src/main.py"]
```

#### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  diary-app:
    build: ./diary_backend
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/src/database
      - ./uploads:/app/src/uploads
      - ./static:/app/src/static
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/usr/share/nginx/html
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - diary-app
    restart: unless-stopped
```

#### 3. 部署命令

```bash
# 构建前端
cd diary_frontend
npm install
npm run build
cp -r dist/* ../static/

# 启动服务
cd ..
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方式三：云平台部署

#### Heroku部署

1. 创建Procfile
```
web: python diary_backend/src/main.py
```

2. 创建runtime.txt
```
python-3.9.18
```

3. 部署命令
```bash
heroku create your-app-name
git push heroku main
```

#### Vercel部署（仅前端）

```bash
cd diary_frontend
npm install -g vercel
vercel --prod
```

## 配置管理

### 环境变量

创建 `.env` 文件：

```bash
# diary_backend/.env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///src/database/app.db
UPLOAD_FOLDER=src/uploads
MAX_CONTENT_LENGTH=16777216

# AI配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1

# Telegram配置
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 数据库初始化

```python
# 初始化脚本 init_db.py
from src.main import app
from src.models.user import db

with app.app_context():
    db.create_all()
    print("数据库初始化完成")
```

## 监控和维护

### 日志管理

```bash
# 查看应用日志
sudo tail -f /var/log/diary-app.log

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 日志轮转配置
sudo nano /etc/logrotate.d/diary-app
```

```
/var/log/diary-app.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 diary diary
}
```

### 备份策略

```bash
#!/bin/bash
# backup.sh - 数据备份脚本

BACKUP_DIR="/home/diary/backups"
APP_DIR="/home/diary/diary-app"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp $APP_DIR/diary_backend/src/database/app.db $BACKUP_DIR/app_$DATE.db

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C $APP_DIR/diary_backend/src uploads/

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $DATE"
```

```bash
# 设置定时备份
crontab -e
# 每天凌晨2点备份
0 2 * * * /home/diary/backup.sh
```

### 性能监控

```bash
# 安装监控工具
sudo apt install htop iotop nethogs -y

# 监控系统资源
htop

# 监控磁盘IO
sudo iotop

# 监控网络
sudo nethogs
```

### 更新部署

```bash
#!/bin/bash
# update.sh - 应用更新脚本

APP_DIR="/home/diary/diary-app"
cd $APP_DIR

# 备份当前版本
./backup.sh

# 拉取最新代码
git pull origin main

# 更新后端依赖
cd diary_backend
source venv/bin/activate
pip install -r requirements.txt

# 构建前端
cd ../diary_frontend
npm install
npm run build
cp -r dist/* ../diary_backend/src/static/

# 重启服务
sudo supervisorctl restart diary-app
sudo systemctl reload nginx

echo "更新完成"
```

## 故障排除

### 常见问题

#### 1. 应用无法启动
```bash
# 检查日志
sudo supervisorctl tail diary-app

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 手动启动测试
cd /home/diary/diary-app/diary_backend
source venv/bin/activate
python src/main.py
```

#### 2. 数据库错误
```bash
# 检查数据库文件权限
ls -la src/database/

# 重新初始化数据库
python init_db.py
```

#### 3. 文件上传失败
```bash
# 检查上传目录权限
ls -la src/uploads/
sudo chown -R diary:diary src/uploads/
sudo chmod -R 755 src/uploads/
```

#### 4. AI功能不工作
- 检查API密钥配置
- 验证网络连接
- 查看API调用日志

#### 5. Telegram推送失败
- 验证Bot Token
- 检查Chat ID
- 测试网络连接

### 性能优化

#### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_diary_entries_timestamp ON diary_entries(timestamp);
CREATE INDEX idx_daily_summaries_date ON daily_summaries(date);
```

#### 2. 静态文件缓存
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### 3. 图片压缩
```python
# 在上传时自动压缩图片
from PIL import Image

def compress_image(image_path, quality=85):
    with Image.open(image_path) as img:
        img.save(image_path, optimize=True, quality=quality)
```

## 安全建议

### 1. 系统安全
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# 禁用root登录
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
```

### 2. 应用安全
- 定期更新依赖包
- 使用强密码
- 启用HTTPS
- 限制文件上传类型和大小
- 定期备份数据

### 3. 数据保护
- 加密敏感配置
- 限制数据库访问权限
- 定期清理日志文件
- 监控异常访问

## 扩展部署

### 多用户支持
如需支持多用户，需要修改：
1. 数据库模型添加用户表
2. 认证系统改为JWT
3. API添加用户隔离
4. 前端添加用户管理

### 高可用部署
1. 负载均衡器（Nginx/HAProxy）
2. 多实例部署
3. 数据库集群（PostgreSQL）
4. Redis缓存
5. 文件存储（MinIO/AWS S3）

### 微服务架构
1. API网关
2. 用户服务
3. 日记服务
4. AI服务
5. 通知服务

---

本部署指南涵盖了从开发环境到生产环境的完整部署流程。根据实际需求选择合适的部署方式，并注意安全和性能优化。

