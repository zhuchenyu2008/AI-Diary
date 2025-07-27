# AI Diary

一个使用AI自动整理的个人日记应用。用户可以上传照片和文字，系统会调用自定义的AI接口分析内容并保存。每天零点后自动汇总前一天的内容生成日记，可通过网页查看、API获取以及 Telegram 推送三种方式访问。

## 安装

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 创建数据库并初始化表结构：

```python
import db
db.init_db()
```

3. 配置环境变量（可在 `.env` 文件中设置）：

```
DB_HOST, DB_USER, DB_PASSWORD, DB_NAME  # MySQL 配置
DIARY_PASSWORD                          # 登录密码（1~4位）
AI_API_URL, AI_API_KEY, AI_MODEL        # AI 接口配置
TELEGRAM_BOT_KEY, TELEGRAM_CHAT_ID      # Telegram 推送配置
SECRET_KEY                              # Flask 会话密钥
```

## 运行

```bash
python app.py
```

访问 `http://localhost:8000` 使用密码登录并记录日记。

## 每日汇总

配置定时任务每天零点运行：

```bash
python daily_summary.py
```

该脚本会整理前一天的所有记录，生成总结并推送到 Telegram。

## API

登陆后可访问 `/api/diary?days=30` 获取最近 30 天内的原始记录。

## 文件结构

- `app.py` Web 应用入口
- `daily_summary.py` 每日汇总脚本
- `db.py` 数据库相关函数
- `ai.py` AI 调用封装
- `telegram_util.py` Telegram 推送
- `templates/` 页面模板
- `static/` 静态资源
