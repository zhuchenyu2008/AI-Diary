# AI日记应用

一个智能AI日记应用，用户可通过文字、图片或图文结合的方式，随时捕捉生活瞬间。应用后端通过AI自动理解内容，并于每日定时或手动将当天全部"瞬间"整理为完整、生动的日记。

## 核心功能

- 多模态记录：支持文字、图片、图文任意组合创建"瞬间"
- AI内容理解：AI自动分析每个"瞬间"并生成情景/情绪描述
- 日记生成：支持手动/自动生成，一天只生成一篇日记
- 多终端适配：支持Web端、API、Telegram推送
- 邮箱为选填字段（用户注册和登录时不强制填写邮箱）

## 技术栈

- 后端：Python FastAPI
- 数据库：MySQL 8.0+
- 对象存储：AWS S3/阿里云OSS
- AI服务：OpenAI/Claude/Gemini
- 任务调度：Celery + Redis
- 推送服务：python-telegram-bot
- 前端：React/Vue.js（预留）

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+
- Redis
- Docker (可选)

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd ai-diary-app
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、AI服务等参数
```

4. 初始化数据库
```bash
python scripts/init_db.py
```

5. 启动应用
```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
docker-compose up -d
```

## API文档

启动应用后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 项目结构

```
ai-diary-app/
├── app/                    # 主应用目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── scripts/               # 脚本文件
├── tests/                 # 测试文件
├── docker-compose.yml     # Docker配置
├── requirements.txt       # Python依赖
└── README.md             # 项目文档
```

## 开发文档

详细的技术文档请参考 [开发文档](docs/development.md)

## 许可证

MIT License 