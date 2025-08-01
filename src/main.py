import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.diary import DiaryEntry, DailySummary, Config, Auth
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.diary import diary_bp
from src.routes.config import config_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'diary_app_secret_key_2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 启用CORS
CORS(app)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(diary_bp, url_prefix='/api/diary')
app.register_blueprint(config_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

def init_default_configs():
    """初始化默认配置"""
    default_configs = [
        {
            'key': 'ai_api_url',
            'value': 'https://api.openai.com/v1',
            'description': 'AI API地址'
        },
        {
            'key': 'ai_api_key',
            'value': '',
            'description': 'AI API密钥'
        },
        {
            'key': 'ai_model',
            'value': 'gpt-3.5-turbo',
            'description': 'AI模型名称'
        },
        {
            'key': 'ai_prompt_template',
            'value': '你是一个温暖贴心的日记助手。请仔细观察用户的日记内容（文字或图片），用温和友善的语调分析用户的活动、情绪和生活状态。请用简洁生动的中文回复，就像一个关心朋友的话语，给出积极正面的观察和建议。',
            'description': 'AI分析提示词模板'
        },
        {
            'key': 'ai_summary_prompt',
            'value': '你是一个贴心的生活记录助手。请根据用户今天的所有日记条目，生成一份温暖的每日总结。总结应该包含：1）今天的主要活动和经历；2）情绪变化和心情轨迹；3）值得纪念的美好时刻；4）简单的生活感悟或鼓励。请用亲切自然的中文表达，就像好朋友在关心地聊天。',
            'description': 'AI每日汇总提示词'
        },
        {
            'key': 'telegram_bot_token',
            'value': '',
            'description': 'Telegram机器人Token'
        },
        {
            'key': 'telegram_chat_id',
            'value': '',
            'description': 'Telegram聊天ID'
        },
        {
            'key': 'telegram_enabled',
            'value': 'false',
            'description': '是否启用Telegram推送'
        }
    ]
    
    for config_data in default_configs:
        existing = Config.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = Config(**config_data)
            db.session.add(config)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_configs()
    
    # 启动定时任务服务
    from src.services.scheduler_service import scheduler_service
    scheduler_service.start(app)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # 停止定时任务服务
        scheduler_service.stop()

