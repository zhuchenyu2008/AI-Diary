# AI-Diary - 智能日记应用

一个新型的日记应用，使用AI大模型来理解您的生活记录，并自动总结成日记，解放双手。采用Liquid Glass设计。

## ✨ 功能特点

### 核心功能
- **多媒体记录**: 支持文字和图片，丰富您的日记内容。
- **实时AI分析**: 在您记录后，AI会立即分析并展示其理解，让您与AI实时互动。
- **每日智能总结**: 每天零点，AI会自动为您生成一份温暖的、个性化的每日总结。
- **时间线与历史视图**: 在时间线视图中查看当天的即时记录，在历史视图中回顾包含每日总结的完整日记。
- **MCP记忆功能**: 内置Model Context Protocol (MCP)，AI能够学习并记住您的偏好、习惯，提供越来越个性化的分析体验。
- **多种查看方式**: 支持网页、API、Telegram推送及Notion同步，随时随地回顾您的记忆。
- **一键Notion集成**: 输入Notion Token即可自动配置，每日总结自动同步到您的Notion工作区。

### 用户体验
- **Liquid Glass设计**: 现代化的玻璃质感界面，结合毛玻璃效果和流畅动画。
- **智能主题**: 支持浅色、深色及跟随系统三种模式，自动适应您的环境。
- **移动端优先**: 为移动设备全面优化，提供流畅的响应式体验。
- **简单认证**: 使用简单的1-4位数字密码，免去繁琐的登录流程。

## 🚀 技术栈

- **前端**: 原生JavaScript (Vanilla JS), CSS3, HTML5
- **后端**: Flask, SQLAlchemy
- **数据库**: SQLite
- **AI**: OpenAI API, 自定义提示词
- **调度**: APScheduler
- **MCP**: Model Context Protocol, 用户记忆管理
- **集成**: Notion API, Telegram Bot API
- **部署**: Docker, Docker Compose

## 🎨 Liquid Glass 设计系统

AI日记的界面采用了自研的 **Liquid Glass** 设计系统，其灵感源于苹果的Human Interface Guidelines。该系统通过真实的毛玻璃效果、流体动画、动态色彩混合和清晰的视觉层次，创造出独特而直观的用户体验。

## 🏁 入门指南

您可以选择在本地运行或使用Docker进行部署。

### 本地开发环境

1.  **克隆项目**
    ```bash
    git clone https://github.com/zhuchenyu2008/AI-Diary
    cd AI-Diary
    ```

2.  **安装依赖**
    ```bash
    # (建议) 创建并激活Python虚拟环境
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    # venv\Scripts\activate # Windows

    # 安装依赖
    pip install -r requirements.txt
    ```

3.  **启动应用**
    ```bash
    python src/main.py
    ```

4.  **访问应用**
    在浏览器中打开 `http://localhost:5000`。默认登录密码为 `1234`。

### Docker 部署

项目提供了 `Dockerfile` 和 `docker-compose.yml`，方便快速部署。

**方式一: 使用 Docker Compose (推荐)**

```bash
docker-compose up -d
```
服务将在 `http://localhost:5000` 上运行。数据库文件将保存在 `./src/database` 目录中。

**方式二: 使用 Docker 命令**

1.  **构建镜像**
    ```bash
    docker build -t ai-diary .
    ```

2.  **运行容器**
    ```bash
    docker run -d \
      --name ai-diary \
      -p 5000:5000 \
      -v $(pwd)/src/database:/app/src/database \
      ai-diary
    ```

## ⚙️ 配置说明

首次运行后，请在应用的设置页面中完成以下配置。

### AI 配置

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `ai_api_url` | AI API地址 | `https://api.openai.com/v1` |
| `ai_api_key` | 您的AI API密钥 | *需要配置* |
| `ai_model` | AI模型名称 | `gpt-3.5-turbo` （经过实测，目前的中文提示词对于doubao-1-5-vision-pro-32k模型的使用体验是最佳的）|
| `ai_prompt_template` | AI分析提示词（已集成MCP记忆功能） | 已配置默认提示词，可按需更改 |
| `ai_summary_prompt` | 每日汇总提示词（已集成MCP记忆功能） | 已配置默认提示词，可按需更改 |

### MCP 配置

MCP (Model Context Protocol) 功能为AI提供了长期记忆能力，让AI能够学习并记住您的偏好、习惯，提供个性化的分析体验。

| 功能 | 说明 |
|---|---|
| **内置记忆服务器** | 系统自动配置usermcp服务器，无需手动配置 |
| **自动学习** | AI在分析日记时会自动提取并记住有价值的个人信息 |
| **记忆分类** | 支持偏好(preference)、习惯(habit)、事实(fact)、情感(emotion)、经历(experience)等类型 |
| **智能运用** | AI在后续分析中会自然地运用已学习的记忆信息 |
| **记忆管理** | 在设置页面的MCP标签中查看和管理AI学习的记忆 |

具体说明：https://github.com/zhuchenyu2008/AI-Diary/blob/main/MCP_USAGE.md

### Telegram 配置 (可选)

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `telegram_bot_token` | 您的机器人Token | *需要配置* |
| `telegram_chat_id` | 您的聊天ID | *需要配置* |
| `telegram_enabled` | 是否启用推送 | `false` |

### Notion 集成 (可选)

Notion 集成功能让您可以将每日总结自动同步到 Notion 工作区，方便长期管理和回顾。

| 配置项 | 说明 | 使用方法 |
|---|---|---|
| **一键配置** | 仅需 Notion Integration Token | 1. 访问 [Notion Integrations](https://www.notion.com/my-integrations)<br>2. 创建新集成，获取 Token<br>3. 在设置页面输入 Token<br>4. 点击"自动配置 Notion" |
| **自动化** | 程序自动完成所有配置 | • 自动搜索或创建"日记"页面<br>• 自动创建标准数据库结构<br>• 自动配置字段映射 |
| **智能同步** | 每日总结自动同步 | • 每天零点后自动同步前日总结<br>• 支持手动同步指定日期<br>• 自动去重，防止重复写入 |
| **数据结构** | 丰富的结构化信息 | • 标题：日记 YYYY-MM-DD<br>• 日期：精确到日<br>• 内容：完整总结文本<br>• 心情：自动识别情绪状态<br>• 标签：智能提取活动标签<br>• 字数：正文长度<br>• 创建方式：AI自动生成 |

**Notion 配置步骤：**
1. 在 [Notion Integrations](https://www.notion.com/my-integrations) 创建集成
2. 复制 Integration Token  
3. 在 AI-Diary 设置页面粘贴 Token
4. 点击"自动配置 Notion"按钮
5. 系统会在工作区创建“日记”页面并在其下新建标准数据库（若已存在“日记/diary”页面，将优先采用搜索到的第一个）
6. 启用同步功能（notion_enabled = true），开始自动同步每日总结

使用说明与行为细节：
- 同步范围：仅同步每日总结，不包含即时记录。
- 写入字段：Name、Date、Content、Mood、Tags、Word Count、Created By（不包含“Summary/摘要”）。
- 查重策略：同一数据库中按 Date 精确查询，若存在则更新第一条，否则创建新页面；不会自动清理重复页面。
- 多数据库/多页面：自动配置每次都会新建数据库并切换配置指向最新库；如需复用旧库，请在配置中手动设置其 database_id。

## 📖 使用指南

1.  **登录**: 使用默认密码 `1234` 登录，建议在设置中修改。
2.  **记录**: 输入文字或上传图片，点击发送。您会看到 "AI理解中..." 的状态，并在片刻后更新为分析结果。
3.  **查看**:
    - **时间线**: 查看当天的所有记录和AI的实时分析。
    - **历史日记**: 回顾过去的所有日记，每日总结会以金色背景高亮显示。
4.  **设置**: 在设置页面配置AI、Telegram、Notion集成、MCP记忆管理以及修改密码。
5.  **MCP记忆**: AI会自动学习您的偏好和习惯，随着使用时间增长，分析会变得越来越个性化和贴心。
6.  **Notion同步**: 配置后每日总结自动同步到Notion；手动生成总结也会同步并推送（若启用）。

## 致谢名单

- 前端UI开发提示词工程：https://github.com/KuekHaoYang/AI-Prompt-Protocols
- 提示词优化工具：https://github.com/linshenkx/prompt-optimizer
- 记忆功能mcp：https://github.com/LSTM-Kirigaya/usermcp
- InstCopilot API：claude-sonnet-4-20250514：710M+tokens
- manus：10k+积分
- code-X；code-x cli
- jules
- 硅基流动：moonshotai/Kimi-K2-Instruct：1000M+tokens
- Any Router：claude-sonnet-4-20250514：16M+tokens
- Your API: claude-sonnet-4-20250514，claude-opus-4-20250514：344k+tokens
- ChatGPT-4o；ChatGPT-o3；ChatGPT-5
- 我的朋友们：JiaHao，汤圆不圆
- 酷狗音乐

## ❓ 常见问题 (FAQ)

**Q: 看不到每日总结内容？**
A: 请确保切换到"历史日记"标签页查看。每日总结只在该视图中以金色背景显示。

**Q: 每日总结何时生成？**
A: 系统在北京时间每天0点自动生成前一天的总结。您也可以在时间线视图中手动触发当日总结。

**Q: AI分析或总结失败？**
A: 请检查AI配置是否正确，确保API密钥有效且账户有足够额度。

**Q: MCP记忆功能如何工作？**
A: AI会在分析您的日记时自动学习并记住重要信息（如食物偏好、兴趣爱好等）。这些记忆会让后续的分析更加个性化和贴心。您可以在设置页面的MCP标签中查看和管理这些记忆。

**Q: Notion同步功能如何使用？**
A: 在设置页面的"Notion 日记同步"区域，输入您的Notion Integration Token，点击"自动配置 Notion"。系统会自动创建页面和数据库，配置完成后每日总结会自动同步到Notion。

**Q: Notion自动配置失败怎么办？**
A: 请确保Token有效且具有创建页面的权限。如果失败，可以手动在Notion中创建名为"日记"的页面，然后重试配置。

## 📚 API 文档

本项目提供了一套完整的RESTful API。详细信息请参阅 [API_Documentation.md](./API_Documentation.md)。

## 📝 更新日志

### v4.1.1 (2025-08-12)
- 修复：Flask 调试重载导致定时任务重复执行的问题（仅在子进程启动调度）。
- 修复：并发防重，按日期文件锁确保每日总结只执行一次；并清理同日旧总结条目。
- 修复：显式使用 Asia/Shanghai 时区，确保北京时间 00:00 触发。
- 变更：移除 Notion 的“Summary/摘要”字段，减少冗余；同步仅写核心字段。
- 修复：Notion 配置加载前清理旧状态，避免沿用过期 Token/ID。

### v4.1.0 (2025-08-11) - Notion集成重大更新
- 🚀 **一键式Notion集成**: 革命性的简化配置体验，用户仅需输入Notion Integration Token
- 🤖 **全自动化配置**: 程序自动搜索或创建"日记"页面，自动创建标准数据库结构
- 📊 **智能数据映射**: 自动提取心情、标签等结构化信息，丰富Notion数据
- 🔄 **无缝同步机制**: 每日总结自动同步到Notion，支持手动同步指定日期
- 🛡️ **完善错误处理**: 多层错误处理，429限流智能重试，确保同步稳定性
- ⚡ **异步性能优化**: 异步执行同步任务，不影响主应用性能
- 🎨 **优雅用户界面**: 现代化配置界面，实时状态反馈和结果展示
- 📝 **API接口完善**: 新增配置状态查询、连接测试、手动同步等完整API
- 🔧 **去重保护机制**: 基于日期的智能去重，防止重复写入
- 📱 **移动端优化**: 配置界面完全适配移动端操作体验

### v4.0.1 (2025-08-11)
- 🛠 修复多处数据库 `db` 导入错误，避免部分接口在运行时异常。
- 🐞 修复系统状态接口中调度器状态的获取方式，`scheduler_running` 现在准确反映 APScheduler 运行状态。
- 📚 同步更新 API 文档：
  - 更正手动生成每日总结接口路径为 `/api/diary/generate-daily-summary`，并说明返回文本格式。
  - 移除文档中未实现的 MCP 记忆创建/更新接口，文档与实际路由保持一致。
  - 补充 MCP 记忆清空与批量删除接口说明。
- 🔐 认证说明完善：首次无密码时会自动设置默认密码 `1234` 并使用安全哈希存储，同时兼容旧版 MD5 哈希验证（仅回退校验，不再用于新密码）。

### v4.0.0 MCP记忆功能集成
- **🧠 MCP记忆系统**: 集成Model Context Protocol，AI具备长期记忆能力
- **🎯 个性化学习**: AI自动学习用户偏好、习惯，提供个性化分析体验
- **🔧 内置记忆服务器**: 自动配置usermcp服务器，支持用户记忆管理
- **📊 记忆分类管理**: 支持偏好、习惯、事实、情感、经历等多种记忆类型
- **⚡ 智能记忆运用**: AI在日记分析和每日总结中自然运用学习到的记忆
- **🛠️ MCP设置界面**: 新增MCP配置页面，支持记忆查看、管理和服务器配置
- **🔐 隐私保护**: 所有记忆数据存储在本地数据库，确保用户隐私安全
- **📈 优化AI提示词**: 更新默认提示词，引导AI更好地使用记忆工具

### v3.0.1 项目优化
- **⏰ 北京时间支持**: 每日总结生成基于北京时间，避免跨时区误差
- **🔧 事件绑定修复**: 调整事件绑定顺序，提升交互稳定性

### v3.0 Liquid Glass界面革新
- **🎨 Liquid Glass设计系统**: 全新的现代化界面设计，采用玻璃质感和流体动画
- **✨ 视觉升级**: 毛玻璃效果、流畅动画、渐变配色和优雅的视觉层次
- **📱 移动端完美适配**: 专为移动设备优化的触摸交互和响应式布局
- **🎯 交互优化**: 改进的按钮布局、间距调整和视觉边界定义
- **🌓 智能主题**: 支持浅色/深色/跟随系统三种主题模式，自动适应用户偏好
- **🔧 界面修复**: 修复了每日总结显示、按钮间距和动画覆盖等问题

### v2.0.2 (2025-08-03)
- ✨ 完善每日总结功能，修复历史日记视图显示问题
- 🔧 修复标签页切换时数据不刷新的bug，添加activeTab依赖
- 🎨 优化每日总结显示样式，金色背景特别标识
- 📱 改进双视图模式：时间线专注日常记录，历史日记包含完整内容
- 🧹 清理调试日志输出，提升应用性能
- 📚 完善README文档，详细说明每日总结功能使用方法
- 🔧 优化前端数据获取逻辑，确保正确传递view参数

### v2.0.1 (2025-07-30)
- 🐛 修复移动端输入框布局问题，防止字符计数挤压发送按钮
- 🔧 修复MCP服务器配置问题，移除必需字段限制，支持标准MCP配置格式
- 🧹 清理MCP页面重复HTML内容，修复执行历史显示异常
- 📱 优化移动端"今日记录"和"历史日记"按钮布局，确保按钮不超出底部框
- 📚 完善MCP配置文档，提供详细的配置方法和示例
- ✨ 支持批量导入MCP服务器配置
- 🔧 改进MCP服务器创建逻辑，支持多种配置方式

### v2.0.0 (2025-07-30)
- ✨ 新增实时AI理解输出功能
- 🔧 优化设置页面逻辑，移除不必要的登录验证
- 📱 全面优化移动端UI和用户体验
- 📷 增强图片功能，支持拍照和上传分离
- 🔌 集成MCP功能，支持获取多维度上下文信息
- 🌐 确保中文网站识别
- 📚 完善API文档和项目文档
- 🐛 修复多个已知问题

### v1.0.0
- 🎉 初始版本发布
- 📝 基础日记记录功能
- 🤖 AI内容分析
- 📊 每日汇总生成
- 📱 基础移动端支持

## 🧑‍💻 面向开发者

### 项目结构
```
AI-Diary/
├── AI prompt word example.md     # AI 提示词示例
├── API_Documentation.md          # API 文档
├── Dockerfile                    # Docker 构建文件
├── LICENSE                       # 许可证
├── README.md                     # 项目说明
├── docker-compose.yml            # Docker Compose 配置
├── requirements.txt              # Python 依赖
├── test_app.py                   # 测试脚本
└── src/                          # 应用源码
    ├── __init__.py               # 包初始化
    ├── main.py                   # 应用入口
    ├── models/                   # 数据模型
    │   ├── diary.py              # 日记模型
    │   ├── mcp.py                # MCP记忆模型
    │   └── user.py               # 用户模型
    ├── routes/                   # API 路由
    │   ├── admin.py              # 管理路由
    │   ├── auth.py               # 认证路由
    │   ├── config.py             # 配置路由
    │   ├── diary.py              # 日记路由
    │   ├── mcp.py                # MCP API路由
    │   └── user.py               # 用户路由
    ├── services/                 # 业务服务
    │   ├── ai_service.py         # AI 服务（集成MCP记忆）
    │   ├── scheduler_service.py  # 调度服务
    │   ├── telegram_service.py   # Telegram 服务
    │   ├── notion_service.py     # Notion 集成服务
    │   └── time_service.py       # 时间工具
    ├── mcp/                      # MCP功能模块
    │   ├── __init__.py           # MCP包初始化
    │   ├── client.py             # MCP客户端管理
    │   └── usermcp_builtin.py    # 内置用户记忆服务
    └── static/                   # 静态文件
        ├── ai_monitor_simple.js  # AI 监控脚本
        ├── config.html           # 设置页面
        ├── favicon.ico           # 网站图标
        ├── index.html            # 主页面
        ├── index_liquid_glass.html # Liquid Glass 演示页面
        ├── mcp.html              # MCP设置页面
        ├── mobile-bottom-fix.css # 移动端底部修复样式
        ├── assets/               # 打包资源
        │   ├── index-DUaNkWBt.js # 前端 JavaScript
        │   └── index-oWMHbS2h.css # 样式文件
        └── js/                   # 自定义 JS 模块
            ├── app.js            # 应用脚本
            └── mcp.js            # MCP功能脚本
```

<img width="7840" height="7050" alt="AI-Diary_architecture" src="https://github.com/user-attachments/assets/e68fdb88-22b2-4725-ad15-75043ffbb989" />



### 未来路线
- 安卓APP开发
- 使单次记录AI通过上下文串联理解
- 更多的推送支持
- MCP服务器扩展和第三方集成（已完成）
- Notion集成功能（已完成）
- 更多云端笔记平台集成（如 Obsidian、飞书等）


### 开发规范
- 后端代码遵循 PEP 8 规范。
- 提交信息请遵循约定式提交 (Conventional Commits) 格式。

### 贡献指南

欢迎任何形式的贡献！无论是Bug修复、功能开发还是文档改进。

1.  Fork 本项目
2.  创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  创建一个 Pull Request

## 📄 许可证

本项目采用 GPL-3.0 license 许可证。
