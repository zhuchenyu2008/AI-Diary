from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.diary import Auth, db
import hashlib

auth_bp = Blueprint('auth', __name__)

def simple_hash(password):
    """简单的密码哈希函数"""
    return hashlib.md5(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        password = data.get('password', '')
        
        # 获取存储的密码哈希
        auth_record = Auth.query.first()
        if not auth_record:
            # 如果没有设置密码，创建默认密码 "1234"
            default_password_hash = simple_hash("1234")
            auth_record = Auth(password_hash=default_password_hash)
            db.session.add(auth_record)
            db.session.commit()
        
        # 验证密码
        if simple_hash(password) == auth_record.password_hash:
            session['authenticated'] = True
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '密码错误'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.pop('authenticated', None)
    return jsonify({'success': True, 'message': '登出成功'})

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查认证状态"""
    authenticated = session.get('authenticated', False)
    return jsonify({'authenticated': authenticated})

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        # 检查是否已认证
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        
        data = request.json
        new_password = data.get('new_password', '')
        
        # 验证密码长度（1-4位）
        if len(new_password) < 1 or len(new_password) > 4:
            return jsonify({'success': False, 'message': '密码长度必须为1-4位'}), 400
        
        # 更新密码
        auth_record = Auth.query.first()
        if not auth_record:
            auth_record = Auth(password_hash=simple_hash(new_password))
            db.session.add(auth_record)
        else:
            auth_record.password_hash = simple_hash(new_password)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
def change_password_with_verification():
    """修改密码（需要验证当前密码）"""
    try:
        # 检查是否已认证
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        
        data = request.json
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # 获取当前密码哈希
        auth_record = Auth.query.first()
        if not auth_record:
            return jsonify({'success': False, 'message': '系统错误：未找到认证记录'}), 500
        
        # 验证当前密码
        if simple_hash(current_password) != auth_record.password_hash:
            return jsonify({'success': False, 'message': '当前密码错误'}), 400
        
        # 验证新密码格式（1-4位数字）
        if not new_password.isdigit() or len(new_password) < 1 or len(new_password) > 4:
            return jsonify({'success': False, 'message': '新密码必须是1-4位数字'}), 400
        
        # 更新密码
        auth_record.password_hash = simple_hash(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

