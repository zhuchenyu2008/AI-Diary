# 杯子日记 (AI Diary)

一个基于AI的智能日记应用，支持文字和图片记录，提供AI理解分析，集成MCP（Model Context Protocol）获取多维度上下文信息。

## ✨ 主要功能

### 🔥 新增功能 (2025-07-30 更新)

- **实时AI理解输出**: 用户发送内容后，AI分析结果实时显示，支持"AI理解中"状态提示
- **优化设置页面**: 移除不必要的登录验证，支持密码重置功能
- **中文网站识别**: 正确识别为中文网站，优化中文用户体验
- **增强图片功能**: 
  - 支持直接调用摄像头拍照
  - 分离"拍照"和"上传图片"按钮
  - 修复纯图片发送的API错误
  - 优化图片显示和处理
- **MCP集成**: 
  - 集成Model Context Protocol
  - 支持时间、位置、天气、系统信息获取
  - 可视化配置界面
  - 权限管理（位置权限、API密钥配置）
- **移动端优化**: 
  - 完全响应式设计
  - 触摸友好的界面
  - 移动端安全区域支持
  - 优化的移动端交互体验

### 📱 核心功能

- **智能日记记录**: 支持文字和图片混合记录
- **AI分析理解**: 基于Gemini AI的内容理解和情感分析
- **实时状态更新**: 动态显示AI分析进度
- **历史记录管理**: 完整的日记历史查看和管理
- **定时总结**: 每日自动生成日记总结
- **多端适配**: 支持桌面端和移动端

## 🏗️ 项目结构

```
AI-Diary/
├── src/                          # 后端源码目录
│   ├── main.py                   # Flask应用入口
│   ├── test_server.py            # 测试服务器
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型和数据库配置
│   │   └── diary.py             # 日记相关模型
│   ├── routes/                   # API路由
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证路由
│   │   ├── diary.py             # 日记相关路由
│   │   ├── config.py            # 配置路由
│   │   ├── admin.py             # 管理员路由
│   │   └── mcp.py               # MCP功能路由
│   ├── services/                 # 业务服务
│   │   ├── __init__.py
│   │   ├── ai_service.py        # AI分析服务
│   │   ├── scheduler_service.py  # 定时任务服务
│   │   └── mcp_service.py       # MCP服务
│   ├── static/                   # 前端静态文件
│   │   ├── index.html           # 主页面
│   │   └── assets/              # CSS、JS等资源文件
│   └── database/                 # 数据库文件目录
│       └── app.db               # SQLite数据库
├── diary_frontend/               # 前端源码目录
│   ├── src/                     # React源码
│   │   ├── App.jsx              # 主应用组件
│   │   ├── App.css              # 样式文件（包含移动端优化）
│   │   ├── main.jsx             # 应用入口
│   │   └── components/          # React组件
│   │       ├── Login.jsx        # 登录组件
│   │       ├── DiaryInput.jsx   # 日记输入组件
│   │       ├── DiaryTimeline.jsx # 日记时间线组件
│   │       ├── HistoryView.jsx  # 历史记录组件
│   │       ├── MCPSettings.jsx  # MCP设置组件
│   │       └── ui/              # UI组件库
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.js           # Vite构建配置
│   └── dist/                    # 构建输出目录
├── docs/                        # 文档目录
│   ├── API_DOCUMENTATION.md     # API文档
│   ├── mcp_research.md          # MCP研究文档
│   └── test_results.md          # 测试结果
├── requirements.txt             # Python依赖
├── deployment_guide.md          # 部署指南
├── todo.md                      # 任务清单
└── README.md                    # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- SQLite 3

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/zhuchenyu2008/AI-Diary.git
   cd AI-Diary
   ```

2. **安装后端依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   # 设置Gemini API密钥
   export GEMINI_API_KEY="your_gemini_api_key_here"
   
   # 可选：设置天气API密钥（用于MCP天气服务）
   export WEATHER_API_KEY="your_weather_api_key_here"
   ```

4. **构建前端**
   ```bash
   cd diary_frontend
   npm install
   npm run build
   cd ..
   
   # 复制构建文件到后端静态目录
   cp -r diary_frontend/dist/* src/static/
   ```

5. **启动应用**
   ```bash
   cd src
   python main.py
   ```

6. **访问应用**
   
   打开浏览器访问 `http://localhost:5000`

### 开发模式

如果需要进行前端开发，可以分别启动前后端：

```bash
# 启动后端
cd src
python main.py

# 新终端启动前端开发服务器
cd diary_frontend
npm run dev
```

## 📱 移动端支持

项目已完全优化移动端体验：

- **响应式设计**: 自适应不同屏幕尺寸
- **触摸优化**: 按钮尺寸适合触摸操作
- **安全区域**: 支持刘海屏等特殊屏幕
- **性能优化**: 移动端滚动和动画优化
- **摄像头支持**: 直接调用移动设备摄像头拍照

## 🔧 配置说明

### AI服务配置

在 `src/services/ai_service.py` 中配置AI服务：

```python
# Gemini API配置
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

### MCP服务配置

MCP（Model Context Protocol）提供多维度上下文信息：

- **时间服务器**: 提供当前时间和日期信息
- **位置服务器**: 获取用户地理位置（需要权限）
- **天气服务器**: 获取天气信息（需要API密钥）
- **系统服务器**: 提供系统信息

在应用设置中可以可视化配置这些服务。

### 数据库配置

项目使用SQLite数据库，数据库文件位于 `src/database/app.db`。首次运行时会自动创建数据库表。

## 📚 API文档

详细的API文档请参考 [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

主要API端点：

- `POST /api/auth/login` - 用户登录
- `POST /api/diary/create` - 创建日记条目
- `GET /api/diary/today` - 获取今日日记
- `GET /api/diary/analysis-status/{entry_id}` - 获取AI分析状态
- `GET /api/mcp/config` - 获取MCP配置
- `POST /api/mcp/test/{server_name}` - 测试MCP服务器

## 🧪 测试

运行测试：

```bash
# 启动测试服务器
cd src
python test_server.py

# 访问 http://localhost:5001 进行测试
```

测试结果记录在 [test_results.md](docs/test_results.md)

## 📦 部署

### 生产环境部署

1. **使用Gunicorn部署**
   ```bash
   pip install gunicorn
   cd src
   gunicorn -w 4 -b 0.0.0.0:5000 main:app
   ```

2. **使用Docker部署**
   ```bash
   # 构建镜像
   docker build -t ai-diary .
   
   # 运行容器
   docker run -p 5000:5000 -e GEMINI_API_KEY=your_key ai-diary
   ```

3. **使用Nginx反向代理**
   
   配置Nginx代理到Flask应用，详见 [deployment_guide.md](deployment_guide.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Gemini AI](https://ai.google.dev/) - AI分析服务
- [React](https://reactjs.org/) - 前端框架
- [Flask](https://flask.palletsprojects.com/) - 后端框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架
- [Model Context Protocol](https://modelcontextprotocol.io/) - 上下文协议

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [项目Issues页面](https://github.com/zhuchenyu2008/AI-Diary/issues)
- 邮箱: [项目维护者邮箱]

---

**最后更新**: 2025-07-30
**版本**: v2.0.0 (包含MCP集成和移动端优化)

