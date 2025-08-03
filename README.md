# AI-Diary - 智能日记应用

一个新型的日记应用，支持用户通过文字和图片记录生活，使用AI大模型理解内容并自动生成日记摘要。本项目已经过全面升级，增加了实时AI理解、MCP集成、移动端优化等多项新功能。

## 🆕 最新更新

### v2.0 主要新功能
- **实时AI理解输出**: 用户发送文字或图片后，今日记录里实时刷新AI的理解输出内容
- **优化设置逻辑**: 移除设置页面不必要的登录验证，优化密码管理流程
- **图片功能增强**: 分离拍照和上传图片功能，支持直接调用摄像头拍照
- **MCP集成**: 内置Model Context Protocol支持，AI可获取时间、位置等多维度信息
- **移动端优化**: 全面优化移动端UI，确保在各种设备上的良好体验
- **中文网站识别**: 确保浏览器正确识别为中文网站

## 功能特点

### 🎯 核心功能
- **多媒体记录**: 支持文字、图片混合记录
- **实时AI理解**: 发送内容后立即显示"AI理解中"状态，完成后实时更新分析结果
- **智能拍照**: 支持直接调用摄像头拍照和从相册上传图片两种方式
- **时间线展示**: 按时间顺序展示日记条目，专注于日常记录流
- **历史日记**: 完整的日记回顾，包含每日总结和普通条目
- **每日总结**: 自动生成每日日记总结，每天0点智能汇总当日记录
- **双视图模式**: 时间线视图查看日常记录，历史日记视图回顾完整内容
- **多种查看方式**: 网页查看、API获取、Telegram推送

### 🤖 AI功能
- 自动分析文字和图片内容
- 智能猜测用户活动和心情
- 可自定义AI提示词模板
- 支持自定义AI API地址和模型
- **MCP集成**: 支持获取用户时间、位置等上下文信息

### 📱 用户体验
- 简洁美观的界面设计
- **全面移动端优化**: 响应式设计，触摸友好的按钮大小
- 实时倒计时显示距离日记汇总时间
- 简单的密码认证（1-4位数字）
- **优化的设置流程**: 无需重复登录验证

### 🔔 推送功能
- Telegram机器人推送每日汇总
- 可配置推送开关
- 支持测试连接功能

### 🔧 MCP功能（核心增强）
- **一键添加**: 支持标准MCP配置格式一键导入
- **内置服务器**: 预置时间、位置、搜索等多种MCP服务器
- **智能配置**: 自动解析标准MCP配置JSON
- **可视化界面**: 完整的Web界面管理MCP服务器
- **执行跟踪**: 详细的历史记录和调试信息
- **协议标准**: 完全兼容Model Context Protocol标准

## 技术架构

### 前端技术栈
- **React 18**: 现代化前端框架
- **Vite**: 快速构建工具
- **Tailwind CSS**: 实用优先的CSS框架
- **shadcn/ui**: 高质量UI组件库
- **Lucide React**: 图标库
- **响应式设计**: 支持桌面端和移动端

### 后端技术栈
- **Flask**: 轻量级Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **OpenAI API**: AI大模型集成
- **APScheduler**: 定时任务调度
- **MCP支持**: Model Context Protocol集成

### 部署架构
- 前后端一体化设计（无需分离构建）
- 静态文件服务
- RESTful API接口
- 支持Docker部署

## 快速开始

### 环境要求
- Python 3.8+

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/zhuchenyu2008/AI-Diary
cd AI-Diary
```

#### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python src/main.py
```

#### 3. 访问应用
- 在浏览器访问 http://localhost:5000
- 静态文件位于 src/static/，无需单独构建前端

### 初始配置

#### 1. 登录密码
默认密码为 `1234`，首次登录后可在设置中修改。

#### 2. AI配置
在应用中配置以下AI参数：
- **API地址**: 默认为 `https://api.openai.com/v1`
- **API密钥**: 需要有效的OpenAI API密钥
- **模型名称**: 默认为 `gpt-3.5-turbo`
- **提示词模板**: 可自定义AI分析提示词

#### 3. Telegram配置（可选）
如需Telegram推送功能：
1. 创建Telegram机器人并获取Bot Token
2. 获取Chat ID
3. 在应用中配置相关参数

#### 4. MCP配置（可选）
通过设置页面的"管理 MCP 服务器"配置：

##### 方式一：使用内置服务器模板
1. 进入设置页面，点击"管理 MCP 服务器"
2. 在"内置服务器模板"部分选择预置的服务器类型
3. 点击"添加"按钮快速配置

##### 方式二：手动配置单个服务器
1. 点击"添加服务器"按钮
2. 选择"手动配置"模式
3. 填写服务器名称、描述
4. 配置启动命令和参数
5. 点击"保存"

##### 方式三：使用标准MCP配置格式（推荐）
1. 点击"添加服务器"按钮
2. 选择"JSON配置"模式
3. **直接粘贴标准MCP配置**，无需任何修改：

```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": [
        "mcp-server-time",
        "--local-timezone=America/New_York"
      ]
    }
  }
}
```

4. 点击"保存"，系统**自动解析并立即添加**所有服务器
5. **支持批量添加**，一次可导入多个服务器配置

##### MCP配置说明
- **服务器名称**: 唯一标识符，用于区分不同的MCP服务器
- **命令**: 启动MCP服务器的命令（如 `uvx`, `npx`, `python` 等）
- **参数**: 命令行参数数组，JSON格式
- **环境变量**: 可选的环境变量配置
- **自动启动**: 是否在应用启动时自动启动该服务器

##### 常用MCP服务器示例

**时间服务器**（纽约时区）：
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    }
  }
}
```

**时间服务器**（自定义时区）：
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
    }
  }
}
```

**文件系统服务器**（自定义目录）：
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "--roots", "./workspace"]
    }
  }
}
```

**Brave搜索服务器**:
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "uvx",
      "args": ["mcp-server-brave-search"]
    }
  }
}
```

**多服务配置示例**:
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    },
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "--roots", "./workspace"]
    },
    "brave-search": {
      "command": "uvx",
      "args": ["mcp-server-brave-search"]
    }
  }
}
```

##### MCP使用流程示意

```mermaid
graph TD
    A[用户点击"添加服务器"] --> B{选择添加方式}
    B -->|内置模板| C[选择预置服务器]
    B -->|手动配置| D[填写服务器参数]
    B -->|JSON配置| E[粘贴标准MCP配置]
    
    C --> F[点击"一键添加"]
    E --> G[系统自动解析]
    D --> H[逐步填写参数]
    
    F --> I[服务器自动创建]
    G --> I
    H --> I
    
    I --> J[可在服务器列表查看]
    J --> K[启动服务器连接]
    K --> L[AI可使用MCP工具]
```

## 项目结构

```
AI-Diary/
├── src/                          # 应用源码
│   ├── main.py                   # 应用入口
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── diary.py              # 日记模型
│   │   ├── config.py             # 配置模型
│   │   ├── user.py               # 用户模型
│   │   └── mcp.py                # MCP模型
│   ├── routes/                   # API路由
│   │   ├── __init__.py
│   │   ├── auth.py               # 认证路由
│   │   ├── diary.py              # 日记路由
│   │   ├── config.py             # 配置路由
│   │   ├── admin.py              # 管理路由
│   │   ├── user.py               # 用户路由
│   │   └── mcp.py                # MCP路由
│   ├── services/                 # 业务服务
│   │   ├── __init__.py
│   │   ├── ai_service.py         # AI服务
│   │   ├── telegram_service.py   # Telegram服务
│   │   └── mcp_service.py        # MCP服务
│   ├── static/                   # 静态文件
│   │   ├── index.html            # 主页面
│   │   ├── config.html           # 设置页面
│   │   ├── mcp.html              # MCP配置页面
│   │   └── assets/               # 静态资源
│   │       ├── index-DUaNkWBt.js # 前端JavaScript
│   │       └── index-oWMHbS2h.css # 样式文件
│   └── database/                 # 数据库文件
│       └── app.db                # SQLite数据库
├── requirements.txt              # Python依赖
├── API_Documentation.md          # API文档
├── test_results.md               # 测试结果
└── README.md                     # 项目说明
```

## API文档

详细的API文档请参考 [API_Documentation.md](./API_Documentation.md)

### 主要接口

#### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/change-password` - 修改密码

#### 日记接口
- `POST /api/diary/entries` - 创建日记条目
- `GET /api/diary/entries/today` - 获取今日条目
- `GET /api/diary/entries/today/analysis-status` - 获取今日条目AI分析状态
- `GET /api/diary/entries` - 获取历史条目（支持view=history参数包含每日总结）
- `POST /api/diary/generate-summary` - 手动生成每日总结
- `GET /api/diary/summaries` - 获取每日汇总

#### 配置接口
- `GET /api/configs` - 获取配置列表
- `PUT /api/configs/{key}` - 更新配置

#### MCP接口
- `GET /api/mcp/servers` - 获取MCP服务器列表
- `POST /api/mcp/servers` - 添加MCP服务器
- `PUT /api/mcp/servers/{id}` - 更新MCP服务器
- `DELETE /api/mcp/servers/{id}` - 删除MCP服务器
- `GET /api/mcp/servers/{id}/tools` - 获取服务器工具列表
- `POST /api/mcp/servers/{id}/tools/{name}/call` - 调用MCP工具

## 配置说明

### AI配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| ai_api_url | AI API地址 | https://api.openai.com/v1 |
| ai_api_key | AI API密钥 | 空（需要配置） |
| ai_model | AI模型名称 | gpt-3.5-turbo |
| ai_prompt_template | AI分析提示词 | 默认提示词 |
| ai_summary_prompt | 每日汇总提示词 | 默认汇总提示词 |

### Telegram配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| telegram_bot_token | 机器人Token | 空（需要配置） |
| telegram_chat_id | 聊天ID | 空（需要配置） |
| telegram_enabled | 是否启用推送 | false |

### MCP配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| mcp_enabled | 是否启用MCP | true |
| mcp_timeout | MCP调用超时时间 | 30秒 |

## 部署指南

### 开发环境部署
1. 按照"快速开始"步骤设置环境
2. 后端运行在 http://localhost:5000

### 生产环境部署

#### 方式一：传统部署
1. 配置反向代理（Nginx）
2. 使用进程管理器（PM2、Supervisor）

#### 方式二：Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY ./ ./
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "src/main.py"]
```

### 数据库备份
SQLite数据库文件位于 `src/database/app.db`，建议定期备份。

## 使用指南

### 基本使用流程

1. **登录**: 使用密码登录系统
2. **记录日记**: 
   - 输入文字内容
   - 可选择拍照或上传图片
   - 点击发送按钮
   - 实时查看AI理解状态
3. **查看记录**: 
   - **时间线视图**：查看当天的日常记录和实时AI分析
   - **历史日记视图**：回顾过往的完整记录，包含每日总结
4. **每日总结查看**：
   - 切换到"历史日记"标签页
   - 每日总结以金色背景特别标识
   - 包含当日活动、情绪分析和生活感悟
5. **AI分析**: 系统自动分析内容并实时显示理解结果
6. **每日总结**: 每天零点自动生成智能日记汇总

### 新功能使用指南

#### 实时AI理解
- 发送内容后立即显示"AI理解中"状态
- AI分析完成后自动更新显示结果
- 保留手动刷新按钮作为备选方案

#### 每日总结功能
- **自动生成**：每天0点自动分析当日所有记录
- **智能内容**：包含主要活动、情绪变化、值得纪念的时刻和生活感悟
- **查看位置**：在"历史日记"标签页中查看
- **特殊标识**：金色背景区分于普通日记条目
- **手动生成**：可在时间线视图手动触发当日总结
- **完整回顾**：提供温暖鼓励的个人化总结

#### 拍照功能
- **拍照按钮**: 直接调用摄像头拍照
- **上传图片按钮**: 从相册选择图片
- 自动申请摄像头权限

#### MCP配置
1. 进入设置页面
2. 点击"管理 MCP 服务器"
3. 添加自定义服务器或启用内置模板
4. 配置服务器参数（URL、认证等）
5. AI将自动获取相关上下文信息

#### 移动端使用
- 界面自动适配移动设备
- 触摸友好的按钮设计
- 防止iOS输入框缩放
- 优化的布局和间距

### 高级功能

#### 自定义AI提示词
可以在配置中修改AI分析的提示词模板，以获得更符合个人需求的分析结果。

#### Telegram推送设置
1. 创建Telegram机器人
2. 获取Bot Token和Chat ID
3. 在应用中配置并启用推送
4. 每日汇总将自动推送到Telegram

#### API集成
应用提供完整的RESTful API，可以集成到其他应用中：
- 支持30天内的日记数据获取
- 提供JSON格式的数据接口
- 支持程序化创建日记条目
- 新增MCP服务器管理API

## 常见问题

### Q: 看不到每日总结内容？
A: 请确保切换到"历史日记"标签页查看。每日总结只在历史日记视图中显示，以金色背景标识。

### Q: 每日总结何时生成？
A: 系统每天0点自动生成前一天的总结。也可在时间线视图中手动点击"现在总结"按钮立即生成。

### Q: 每日总结生成失败？
A: 请检查AI API配置是否正确，确保API密钥有效且有足够的额度。每日总结需要较多的AI资源。

### Q: AI分析功能不工作？
A: 请检查AI API配置是否正确，确保API密钥有效且有足够的额度。

### Q: 实时AI理解不更新？
A: 请检查网络连接和API配置，确保后端服务正常运行。

### Q: 拍照功能无法使用？
A: 请确保浏览器已授权摄像头权限，并使用HTTPS协议访问。

### Q: Telegram推送失败？
A: 请检查Bot Token和Chat ID是否正确，并确保机器人已启动对话。

### Q: 图片上传失败？
A: 请确保图片大小不超过16MB，格式为常见的图片格式。

### Q: 如何修改密码？
A: 登录后进入设置页面，在密码管理部分修改密码。

### Q: MCP服务器连接失败？
A: 请检查以下几点：
1. 确保MCP服务器命令和参数配置正确
2. 检查服务器是否已安装（如 `uvx` 或 `npx` 命令是否可用）
3. 验证服务器路径和权限设置
4. 查看执行历史中的错误信息
5. 确保服务器支持标准的MCP协议

### Q: MCP配置格式错误？
A: 请确保使用正确的JSON格式：
- 使用双引号包围字符串
- 数组参数使用方括号 `[]`
- 检查JSON语法是否正确
- 参考文档中的示例配置

### Q: 如何添加自定义MCP服务器？
A: 有三种方式：
1. **内置模板**: 选择预置的服务器类型快速添加
2. **手动配置**: 逐个填写服务器参数
3. **JSON配置**: 使用标准MCP配置格式批量添加

### Q: MCP服务器无法启动？
A: 请检查：
1. 命令是否在系统PATH中可用
2. 参数格式是否正确（JSON数组格式）
3. 环境变量是否正确配置
4. 服务器是否需要特定的依赖或权限

### Q: 移动端显示异常？
A: 请清除浏览器缓存并刷新页面，确保加载最新的CSS样式。

### Q: 数据如何备份？
A: 备份 `src/database/app.db` 文件即可。

## 开发指南

### 添加新功能
1. 后端：在 `routes/` 目录添加新的路由
2. 服务：在 `services/` 目录添加业务逻辑
3. 数据库：在 `models/` 目录添加新的模型
4. 前端：修改对应的HTML和JavaScript文件

### 代码规范
- 后端遵循PEP 8规范
- 前端遵循现代JavaScript标准
- 提交信息使用约定式提交格式

### 测试
- 后端：使用pytest进行单元测试
- API：使用Postman或类似工具测试
- 前端：在多种设备和浏览器上测试

### MCP开发
- 遵循MCP协议标准
- 参考官方文档：https://modelcontextprotocol.io/docs/
- 使用标准的JSON-RPC 2.0格式

## 更新日志

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

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 贡献类型
- 🐛 Bug修复
- ✨ 新功能开发
- 📚 文档改进
- 🎨 UI/UX优化
- ⚡ 性能优化
- 🔧 配置和工具改进

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 致谢

感谢所有为这个项目做出贡献的开发者和用户！

特别感谢：
- OpenAI 提供的AI API服务
- Model Context Protocol 社区
- React 和 Flask 开源社区

---

感谢使用AI日记！希望这个应用能帮助您更好地记录和回顾生活的美好时光。如有任何问题或建议，欢迎通过GitHub Issues联系我们。

