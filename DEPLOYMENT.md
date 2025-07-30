# 部署指南

本文档提供了AI日记项目的详细部署指南，包括开发环境、测试环境和生产环境的部署方法。

## 📋 部署前准备

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+) / macOS / Windows
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **数据库**: SQLite 3 (默认) / PostgreSQL / MySQL (可选)
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 1GB 可用空间

### 必需的API密钥

1. **Gemini AI API密钥** (必需)
   - 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 创建新的API密钥
   - 记录密钥用于后续配置

2. **天气API密钥** (可选，用于MCP天气服务)
   - 访问 [OpenWeatherMap](https://openweathermap.org/api)
   - 注册并获取免费API密钥

## 🔧 开发环境部署

### 1. 克隆项目

```bash
git clone https://github.com/zhuchenyu2008/AI-Diary.git
cd AI-Diary
```

### 2. 后端环境配置

```bash
# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 前端环境配置

```bash
cd diary_frontend
npm install
cd ..
```

### 4. 环境变量配置

创建 `.env` 文件：

```bash
# 在项目根目录创建 .env 文件
cat > .env << EOF
# AI服务配置
GEMINI_API_KEY=your_gemini_api_key_here

# 可选：天气API配置
WEATHER_API_KEY=your_weather_api_key_here

# Flask配置
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# 数据库配置
DATABASE_URL=sqlite:///database/app.db
EOF
```

### 5. 构建前端

```bash
cd diary_frontend
npm run build
cd ..

# 复制构建文件到后端静态目录
cp -r diary_frontend/dist/* src/static/
```

### 6. 初始化数据库

```bash
cd src
python -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"
```

### 7. 启动开发服务器

```bash
cd src
python main.py
```

访问 `http://localhost:5000` 查看应用。

## 🧪 测试环境部署

### 使用测试服务器

```bash
cd src
python test_server.py
```

这将启动一个简化的测试服务器，用于验证前端功能。

### 运行测试

```bash
# 功能测试
python -m pytest tests/ -v

# 前端测试
cd diary_frontend
npm test
```

## 🚀 生产环境部署

### 方法一：使用Gunicorn (推荐)

1. **安装Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **创建Gunicorn配置文件**
   ```bash
   cat > gunicorn.conf.py << EOF
   bind = "0.0.0.0:5000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   EOF
   ```

3. **启动应用**
   ```bash
   cd src
   gunicorn -c ../gunicorn.conf.py main:app
   ```

### 方法二：使用Docker

1. **创建Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   # 安装Node.js
   RUN apt-get update && apt-get install -y curl && \
       curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
       apt-get install -y nodejs

   # 复制项目文件
   COPY . .

   # 安装Python依赖
   RUN pip install -r requirements.txt

   # 构建前端
   RUN cd diary_frontend && npm install && npm run build && \
       cp -r dist/* ../src/static/

   # 暴露端口
   EXPOSE 5000

   # 启动应用
   CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.main:app"]
   ```

2. **构建和运行**
   ```bash
   # 构建镜像
   docker build -t ai-diary .

   # 运行容器
   docker run -d \
     --name ai-diary \
     -p 5000:5000 \
     -e GEMINI_API_KEY=your_key \
     -v $(pwd)/data:/app/src/database \
     ai-diary
   ```

### 方法三：使用Docker Compose

1. **创建docker-compose.yml**
   ```yaml
   version: '3.8'

   services:
     ai-diary:
       build: .
       ports:
         - "5000:5000"
       environment:
         - GEMINI_API_KEY=${GEMINI_API_KEY}
         - WEATHER_API_KEY=${WEATHER_API_KEY}
       volumes:
         - ./data:/app/src/database
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

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

## 🌐 Nginx反向代理配置

### 基础配置

```nginx
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

    # 静态文件缓存
    location /static/ {
        proxy_pass http://127.0.0.1:5000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API请求
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Content-Type application/json;
    }
}
```

### HTTPS配置 (使用Let's Encrypt)

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控和日志

### 应用监控

1. **健康检查端点**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **日志配置**
   ```python
   # 在main.py中添加
   import logging
   from logging.handlers import RotatingFileHandler

   if not app.debug:
       file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
       file_handler.setFormatter(logging.Formatter(
           '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
       ))
       file_handler.setLevel(logging.INFO)
       app.logger.addHandler(file_handler)
   ```

### 系统监控

使用systemd管理服务：

```bash
# 创建服务文件
sudo cat > /etc/systemd/system/ai-diary.service << EOF
[Unit]
Description=AI Diary Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/AI-Diary/src
Environment=PATH=/path/to/AI-Diary/venv/bin
ExecStart=/path/to/AI-Diary/venv/bin/gunicorn -c ../gunicorn.conf.py main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl enable ai-diary
sudo systemctl start ai-diary
sudo systemctl status ai-diary
```

## 🔒 安全配置

### 1. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 应用安全

- 使用强密码和安全的SECRET_KEY
- 定期更新依赖包
- 启用HTTPS
- 配置适当的CORS策略
- 实施速率限制

### 3. 数据备份

```bash
# 创建备份脚本
cat > backup.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/ai-diary"
mkdir -p $BACKUP_DIR

# 备份数据库
cp src/database/app.db $BACKUP_DIR/app_$DATE.db

# 备份上传的图片
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz src/static/uploads/

# 清理7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 添加到crontab
crontab -e
# 添加：0 2 * * * /path/to/backup.sh
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /path/to/AI-Diary
   sudo chmod -R 755 /path/to/AI-Diary
   ```

3. **数据库连接失败**
   - 检查数据库文件权限
   - 确认数据库路径正确
   - 查看应用日志

4. **前端资源404**
   - 确认前端已正确构建
   - 检查静态文件路径
   - 验证Nginx配置

### 日志查看

```bash
# 应用日志
tail -f logs/app.log

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 系统服务日志
sudo journalctl -u ai-diary -f
```

## 📈 性能优化

### 1. 数据库优化

- 定期清理旧数据
- 添加适当的索引
- 考虑使用PostgreSQL替代SQLite

### 2. 缓存配置

- 使用Redis缓存AI分析结果
- 配置静态文件缓存
- 实施API响应缓存

### 3. 负载均衡

对于高流量场景，考虑使用多个应用实例：

```nginx
upstream ai_diary {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location / {
        proxy_pass http://ai_diary;
    }
}
```

---

如有部署问题，请查看项目Issues或联系维护者。

