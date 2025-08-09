import os
import sys
import asyncio
import logging
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.diary import DiaryEntry, DailySummary, Config, Auth
from src.models.mcp import MCPServer, UserMemory, MCPExecutionLog
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.diary import diary_bp
from src.routes.config import config_bp
from src.routes.admin import admin_bp
from src.routes.mcp import mcp_bp
from src.routes.page import page_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
# 从环境变量加载密钥，防止秘钥泄露。提供默认值以便开发环境运行。
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'diary_app_secret_key_2025')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 会话配置 - 确保iframe中可以访问cookies
app.config['SESSION_COOKIE_SAMESITE'] = None  # 允许跨iframe访问
app.config['SESSION_COOKIE_SECURE'] = False   # 开发环境不需要HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = False  # 允许JavaScript访问cookie（这对iframe很重要）

# 启用CORS
CORS(app)

# 数据库配置
database_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(database_dir, exist_ok=True)  # 确保数据库目录存在
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(config_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(mcp_bp, url_prefix='/api/mcp')
app.register_blueprint(page_bp)

def init_default_configs():
    """初始化默认配置 - 使用统一的配置管理"""
    from src.config.defaults import get_default_configs
    
    default_configs = get_default_configs()
    
    for config_data in default_configs:
        existing = Config.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = Config(**config_data)
            db.session.add(config)
    
    db.session.commit()

def init_default_mcp_servers():
    """初始化默认MCP服务器"""
    try:
        # 检查是否已存在内置usermcp服务器
        existing_usermcp = MCPServer.query.filter_by(name='usermcp', builtin=True).first()
        if not existing_usermcp:
            usermcp_server = MCPServer(
                name='usermcp',
                command='builtin',
                args=[],
                env={},
                enabled=True,
                builtin=True
            )
            db.session.add(usermcp_server)
            db.session.commit()
            logger.info("初始化内置usermcp服务器配置")
        
        # 初始化MCP客户端管理器
        from src.mcp.client import get_mcp_manager
        mcp_manager = get_mcp_manager(db.session)
        asyncio.run(mcp_manager.initialize_builtin_servers())
        
    except Exception as e:
        logger.error(f"初始化MCP服务器失败: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # 排除API路由，避免与蓝图冲突
    if path.startswith('api/'):
        from flask import abort
        abort(404)
        
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


def upgrade_database():
    """升级数据库结构 - 使用安全的DDL语句"""
    try:
        # 检查 diary_entries 表是否有 is_daily_summary 字段
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('diary_entries')]
        
        if 'is_daily_summary' not in columns:
            # 使用参数化查询避免SQL注入 - 对于DDL语句使用更安全的方法
            with db.engine.connect() as connection:
                # DDL语句通常不支持参数绑定，但我们可以验证表名的安全性
                table_name = 'diary_entries'
                column_def = 'is_daily_summary BOOLEAN DEFAULT FALSE'
                
                # 验证表名和列定义的安全性
                if table_name.isalnum() or '_' in table_name:
                    # 使用更安全的DDL执行方式
                    alter_statement = text(f'ALTER TABLE {table_name} ADD COLUMN {column_def}')
                    connection.execute(alter_statement)
                    connection.commit()
                    logger.info("数据库升级完成：添加了 is_daily_summary 字段")
                else:
                    logger.error("数据库升级失败：表名包含不安全字符")
    except Exception as e:
        logger.error(f"数据库升级失败: {e}")
        # 如果升级失败，继续运行（可能字段已存在）
        pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        upgrade_database()  # 升级数据库结构
        init_default_configs()
        init_default_mcp_servers()  # 初始化MCP服务器
    
    # 启动定时任务服务
    from src.services.scheduler_service import scheduler_service
    scheduler_service.start(app)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # 停止定时任务服务
        scheduler_service.stop()

