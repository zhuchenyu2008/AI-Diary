# AI 智能日记

一个功能完整、代码优雅、易于部署和使用的AI智能日记Web应用。

## 功能特性

- **事件记录**: 支持通过文本和图片记录日常生活中的点滴事件。
- **自动汇总**: 每日零点，AI自动将当天的所有事件汇总成一篇完整的日记。
- **Telegram推送**: 生成的日记会自动通过Telegram Bot推送到你的私人频道。
- **历史回顾**: 随时可以回顾和检索过去任何一天的日记。
- **响应式设计**: 简洁美观的前端界面，在桌面和移动设备上均有良好体验。
- **安全简单**: 单用户模式，通过简单的PIN码登录，无需复杂的账户系统。

## 技术栈

- **后端**: Python, Flask, Flask-APScheduler, MySQL
- **前端**: Vue.js, Vue Router, Axios
- **数据库**: MySQL
- **AI集成**: 任何兼容OpenAI API格式的模型服务
- **推送**: Telegram Bot API

## 项目结构

```
.
├── backend/         # 后端代码
│   ├── app.py       # Flask主应用
│   ├── ai_service.py # AI服务模块
│   ├── requirements.txt # Python依赖
│   └── config.ini.template # 配置文件模板
├── frontend/        # 前端代码
│   ├── src/
│   ├── package.json # Node.js依赖
│   └── ...
└── docs/            # 文档和数据库脚本
    ├── README.md    # 本文档
    ├── API.md       # API接口文档
    └── database.sql # 数据库初始化脚本
```

## 部署指南

### 1. 环境准备

- Python 3.6+
- Node.js 14+ 和 npm
- MySQL 5.7+
- 一个Telegram Bot（通过 @BotFather 创建）

### 2. 后端部署

1. **进入后端目录**:
   ```bash
   cd backend
   ```
2. **创建并激活虚拟环境** (推荐):
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```
3. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
4. **配置**:
   - 复制配置文件模板: `cp config.ini.template config.ini`
   - 编辑 `config.ini` 文件，填入你的数据库、AI模型、Telegram Bot和登录密码等信息。
5. **初始化数据库**:
   - 登录你的MySQL服务器。
   - 执行 `docs/database.sql` 脚本来创建数据库和表。
6. **启动后端服务**:
   ```bash
   python app.py
   ```
   服务将默认运行在 `http://localhost:5000`。

### 3. 前端部署

1. **进入前端目录**:
   ```bash
   cd frontend
   ```
2. **安装依赖**:
   ```bash
   npm install
   ```
3. **启动前端开发服务**:
   ```bash
   npm run dev
   ```
   应用将运行在 `http://localhost:5173`。

### 4. 生产环境部署

对于生产环境，建议使用Gunicorn + Nginx来部署后端Flask应用，并使用`npm run build`构建前端静态文件后由Nginx提供服务。

## 使用说明

1. 打开浏览器，访问前端地址（例如 `http://localhost:5173`）。
2. 在登录页面输入你在 `config.ini` 中设置的 `LOGIN_PASSWORD`。
3. **主页**:
   - 在文本框中输入文字，或上传一张图片，点击“Record Event”来记录一个事件。
   - 页面下方会实时显示今天记录的所有事件。
   - 顶部的倒计时显示距离下一次AI自动总结还有多长时间。
4. **历史页**:
   - 使用日期选择器可以查看指定日期的日记总结。
   - 页面下方会列出所有已生成总结的日期，点击即可查看。
5. **每日自动任务**:
   - 每天 `00:00`，系统会自动获取前一天的所有事件，调用AI模型生成总结，存入数据库，并通过Telegram Bot发送给你。

---

祝你使用愉快！
