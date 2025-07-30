#!/bin/bash

echo "AI日记快速启动脚本"
echo "===================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 检查Node.js版本
if ! command -v node &> /dev/null; then
    echo "错误: 需要安装Node.js 16+"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 构建前端
echo "构建前端..."
cd diary_frontend
npm install
npm run build
cd ..

# 复制前端文件
echo "复制前端文件..."
cp -r diary_frontend/dist/* src/static/

# 初始化数据库
echo "初始化数据库..."
cd src
python3 -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"

echo "启动应用..."
python3 main.py
