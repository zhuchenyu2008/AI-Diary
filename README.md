# 杯子日记 - 智能日记应用

一个新型的日记应用，支持用户通过文字和图片记录生活，使用AI大模型理解内容并自动生成日记摘要。

## 功能特点

### 🎯 核心功能
- **多媒体记录**: 支持文字、图片混合记录
- **AI智能理解**: 自动分析用户活动和心情
- **时间线展示**: 按时间顺序展示日记条目
- **每日汇总**: 自动生成每日日记总结
- **多种查看方式**: 网页查看、API获取、Telegram推送

### 🤖 AI功能
- 自动分析文字和图片内容
- 智能猜测用户活动和心情
- 可自定义AI提示词模板
- 支持自定义AI API地址和模型

### 📱 用户体验
- 简洁美观的界面设计
- 响应式设计，支持移动端
- 实时倒计时显示距离日记汇总时间
- 简单的密码认证（1-4位数字）

### 🔔 推送功能
- Telegram机器人推送每日汇总
- 可配置推送开关
- 支持测试连接功能

## 技术架构

### 前端技术栈
- **React 18**: 现代化前端框架
- **Vite**: 快速构建工具
- **Tailwind CSS**: 实用优先的CSS框架
- **shadcn/ui**: 高质量UI组件库
- **Lucide React**: 图标库

### 后端技术栈
- **Flask**: 轻量级Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **OpenAI API**: AI大模型集成
- **APScheduler**: 定时任务调度

### 部署架构
- 前后端分离设计
- 静态文件服务
- RESTful API接口
- 支持Docker部署

## 快速开始

### 环境要求
- Python 3.8+

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd diary-app
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


- 在浏览器访问 http://localhost:5000（静态文件位于 src/static/，无需单独构建前端）
### 初始配置

#### 1. 登录密码
默认密码为 `1234`，可在应用中修改。

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

## 项目结构

```
diary-app/
├── src/                  # 应用源码
│   ├── main.py           # 应用入口
│   ├── models/           # 数据模型
│   ├── routes/           # API路由
│   ├── services/         # 业务服务
│   └── static/           # 静态文件
├── requirements.txt      # Python依赖
├── API_Documentation.md  # API文档
└── README.md             # 项目说明
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
- `GET /api/diary/entries` - 获取历史条目
- `GET /api/diary/summaries` - 获取每日汇总

#### 配置接口
- `GET /api/configs` - 获取配置列表
- `PUT /api/configs/{key}` - 更新配置

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
   - 可选择上传图片
   - 点击发送按钮
3. **查看记录**: 
   - 今日记录：查看当天的所有条目
   - 历史日记：查看过往的日记汇总
4. **AI分析**: 系统自动分析内容并显示理解结果
5. **每日汇总**: 每天零点自动生成日记汇总

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

## 常见问题

### Q: AI分析功能不工作？
A: 请检查AI API配置是否正确，确保API密钥有效且有足够的额度。

### Q: Telegram推送失败？
A: 请检查Bot Token和Chat ID是否正确，并确保机器人已启动对话。

### Q: 图片上传失败？
A: 请确保图片大小不超过16MB，格式为常见的图片格式。

### Q: 如何修改密码？
A: 在登录后，可以通过API接口或直接修改数据库来更改密码。

### Q: 数据如何备份？
A: 备份 `src/database/app.db` 文件即可。

## 开发指南

### 添加新功能
1. 后端：在 `routes/` 目录添加新的路由
3. 数据库：在 `models/` 目录添加新的模型

### 代码规范
- 后端遵循PEP 8规范
- 提交信息使用约定式提交格式

### 测试
- 后端：使用pytest进行单元测试
- API：使用Postman或类似工具测试

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 加入讨论群

## 更新日志

### v1.0.0 (2025-07-28)
- 🎉 初始版本发布
- ✨ 支持文字和图片日记记录
- 🤖 集成AI智能分析功能
- 📱 实现响应式前端界面
- 🔔 支持Telegram推送
- ⏰ 自动每日汇总功能
- 📚 完整的API文档

---

感谢使用杯子日记！希望这个应用能帮助您更好地记录和回顾生活的美好时光。

