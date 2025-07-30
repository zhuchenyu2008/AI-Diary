FROM python:3.9-slim

WORKDIR /app

# 安装Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 构建前端
RUN cd diary_frontend && npm install && npm run build && \
    cp -r dist/* ../src/static/ && \
    cd .. && rm -rf diary_frontend/node_modules

# 创建数据库目录
RUN mkdir -p src/database

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python3", "src/main.py"]
