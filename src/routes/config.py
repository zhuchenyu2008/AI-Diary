from flask import Blueprint, jsonify, request, session
from src.models.diary import Config, db
from src.utils.auth import require_auth

config_bp = Blueprint('config', __name__)

@config_bp.route('/configs', methods=['GET'])
def get_configs():
    """获取所有配置 - 需要认证，但返回友好的错误信息"""
    if not session.get('authenticated', False):
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
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
    """初始化默认配置 - 使用统一的配置管理"""
    try:
        from src.config.defaults import get_default_configs
        
        default_configs = get_default_configs()
        
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

