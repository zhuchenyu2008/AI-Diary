from flask import Blueprint, jsonify, request, session
from src.models.diary import Config
from src.models.user import db
from src.services.ai_service import ai_service
from src.services.telegram_service import telegram_service
from src.services.scheduler_service import scheduler_service
from datetime import datetime, date
from src.services.time_service import time_service
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def require_auth(f):
    """认证装饰器，要求用户已登录。使用wraps保留元数据。"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)

    return decorated_function

@admin_bp.route('/test-ai', methods=['POST'])
@require_auth
def test_ai():
    """测试AI连接"""
    try:
        data = request.json or {}
        test_text = data.get('text', '测试文本')

        # 先测试连通性
        success, message = ai_service.test_connection()
        if not success:
            return jsonify({'success': False, 'message': message}), 500

        result = ai_service.analyze_entry(test_text)

        if result.startswith('AI分析失败') or result == 'AI服务未配置':
            return jsonify({'success': False, 'message': result}), 500

        return jsonify({
            'success': True,
            'message': 'AI测试成功',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'AI测试失败: {str(e)}'}), 500

@admin_bp.route('/test-telegram', methods=['POST'])
@require_auth
def test_telegram():
    """测试Telegram连接"""
    try:
        # 重新加载Telegram配置
        telegram_service._load_config()

        # 测试连接
        success, message = telegram_service.test_connection()

        if not success:
            return jsonify({'success': False, 'message': message}), 500

        test_success = telegram_service.send_message("🧪 这是一条测试消息，来自杯子日记")
        if test_success:
            return jsonify({'success': True, 'message': '测试消息发送成功'})
        else:
            return jsonify({'success': False, 'message': '连接成功但发送消息失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Telegram测试失败: {str(e)}'}), 500

@admin_bp.route('/generate-summary', methods=['POST'])
@require_auth
def generate_summary():
    """手动生成日记汇总"""
    try:
        data = request.json
        date_str = data.get('date')
        
        if not date_str:
            return jsonify({'success': False, 'message': '请提供日期'}), 400
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': '日期格式错误，请使用YYYY-MM-DD'}), 400
        
        # 手动生成汇总
        success, message = scheduler_service.generate_summary_manually(target_date)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成汇总失败: {str(e)}'}), 500

@admin_bp.route('/reload-services', methods=['POST'])
@require_auth
def reload_services():
    """重新加载服务配置"""
    try:
        # 重新加载AI服务配置
        ai_service._load_config()
        
        # 重新加载Telegram服务配置
        telegram_service._load_config()
        
        return jsonify({
            'success': True,
            'message': '服务配置重新加载成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'重新加载失败: {str(e)}'}), 500

@admin_bp.route('/system-status', methods=['GET'])
@require_auth
def system_status():
    """获取系统状态"""
    try:
        # 检查AI配置
        ai_configured = bool(ai_service.client)
        
        # 检查Telegram配置
        telegram_configured = telegram_service.enabled
        
        # 检查调度器状态
        scheduler_running = scheduler_service.scheduler.running
        
        return jsonify({
            'success': True,
            'status': {
                'ai_configured': ai_configured,
                'telegram_configured': telegram_configured,
                'scheduler_running': scheduler_running,
                'timestamp': time_service.get_beijing_time().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取系统状态失败: {str(e)}'}), 500
