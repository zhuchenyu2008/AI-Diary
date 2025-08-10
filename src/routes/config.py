from flask import Blueprint, jsonify, request, session
from src.models.diary import Config, db
from functools import wraps

config_bp = Blueprint('config', __name__)

def require_auth(f):
    """认证装饰器，要求用户已登录。

    使用functools.wraps保留原函数的元数据，便于调试与文档生成。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)

    return decorated_function

@config_bp.route('/configs', methods=['GET'])
@require_auth
def get_configs():
    """获取所有配置"""
    try:
        configs = Config.query.all()
        return jsonify({
            'success': True,
            'configs': [config.to_dict() for config in configs]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@config_bp.route('/configs/<string:key>', methods=['GET'])
@require_auth
def get_config(key):
    """获取指定配置"""
    try:
        config = Config.query.filter_by(key=key).first()
        if config:
            return jsonify({
                'success': True,
                'config': config.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@config_bp.route('/configs', methods=['POST'])
@require_auth
def create_or_update_configs():
    """创建或更新多个配置"""
    try:
        configs_data = request.json
        if not isinstance(configs_data, list):
            return jsonify({'success': False, 'message': '无效的数据格式，需要一个配置列表'}), 400

        updated_configs = []
        for data in configs_data:
            key = data.get('key')
            value = data.get('value')

            if not key:
                continue

            config = Config.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value)
                db.session.add(config)
            updated_configs.append(config)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置已成功保存',
            'configs': [c.to_dict() for c in updated_configs]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@config_bp.route('/configs/<string:key>', methods=['DELETE'])
@require_auth
def delete_config(key):
    """删除配置"""
    try:
        config = Config.query.filter_by(key=key).first()
        if not config:
            return jsonify({'success': False, 'message': '配置不存在'}), 404
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置删除成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@config_bp.route('/configs/init-defaults', methods=['POST'])
@require_auth
def init_default_configs():
    """初始化默认配置"""
    try:
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
                'value': '请分析这个用户的日记内容（包括文字和图片），猜测用户在做什么，用简洁的中文描述用户的活动和心情。',
                'description': 'AI分析提示词模板'
            },
            {
                'key': 'ai_summary_prompt',
                'value': '请根据用户今天的所有日记条目，生成一份完整的日记总结。总结应该包含今天的主要活动、心情变化和重要事件。',
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
        
        created_count = 0
        for config_data in default_configs:
            existing = Config.query.filter_by(key=config_data['key']).first()
            if not existing:
                config = Config(**config_data)
                db.session.add(config)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功初始化 {created_count} 个默认配置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

