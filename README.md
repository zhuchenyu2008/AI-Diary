# AI Diary

一个基于 Flask 的个人日记应用，结合 AI 自动分析和整理每天的内容。用户可上传照片或文本，AI 会理解内容并生成总结。每日零点自动归纳前一天的记录，可通过网页、API 或 Telegram 消息查看。

## 环境准备

1. **安装 Python 3.8+**，推荐在虚拟环境中运行。
2. **克隆仓库并进入目录**：
   ```bash
   git clone <仓库地址>
   cd AI-Diary
   ```
3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

## 数据库配置

1. 在 MySQL 中创建数据库和用户（示例）：
   ```sql
   CREATE DATABASE diary DEFAULT CHARSET utf8mb4;
   CREATE USER 'diary'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON diary.* TO 'diary'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. 在项目根目录创建 `.env` 文件，填入以下变量（示例值仅供参考）：
   ```env
   DB_HOST=localhost
   DB_USER=diary
   DB_PASSWORD=password
   DB_NAME=diary

   DIARY_PASSWORD=1234             # 登录密码，1~4 位
   AI_API_URL=https://api.openai.com/v1/chat/completions
   AI_API_KEY=你的API密钥
   AI_MODEL=gpt-3.5-turbo

   TELEGRAM_BOT_KEY=你的BotKey
   TELEGRAM_CHAT_ID=你的ChatID

   SECRET_KEY=随意的字符串
   ```

## 初始化数据库

运行以下命令创建必要的表：
```bash
python -c "import db; db.init_db()"
```

## 运行应用

1. 启动服务：
   ```bash
   python app.py
   ```
2. 打开浏览器访问 `http://localhost:8000`，输入 `.env` 中设置的 `DIARY_PASSWORD` 登录。
3. 点击“记录新的内容”可上传图片或输入文字。提交后 AI 会自动分析并保存记录。
4. 首页可查看系统每日生成的总结，最多保留一年内的内容。

## 每日自动汇总

将 `daily_summary.py` 设置为每天零点执行，示例 cron 语法：
```bash
0 0 * * * /usr/bin/python /path/to/daily_summary.py
```
脚本会整理前一天的记录，通过 AI 生成总结并保存在数据库中，同时推送到 Telegram（若配置了相关变量）。

## API 使用

在登录状态下访问：
```
http://localhost:8000/api/diary?days=30
```
参数 `days` 表示返回多少天内的原始记录，最大 30 天。返回结果为 JSON 数组，可用于自定义分析或备份。

## 目录说明

- `app.py`              Flask Web 应用入口
- `daily_summary.py`    每日汇总脚本
- `db.py`               数据库操作封装
- `ai.py`               AI 调用逻辑
- `telegram_util.py`    Telegram 推送工具
- `templates/`          前端页面模板
- `static/`             静态资源（CSS 等）

完成以上步骤即可开始使用 AI Diary 记录并自动整理你的日常生活。若需更换 AI 模型或接口，只需修改 `.env` 中的相关配置即可。
