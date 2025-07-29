from flask import Blueprint, jsonify, request, session
from src.models.diary import Auth, db
import hashlib

auth_bp = Blueprint('auth', __name__)

def simple_hash(password):
    """简单的密码哈希函数"""
    return hashlib.md5(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """进入应用的登录"""
    try:
        data = request.json
        password = data.get('password', '')

        auth_record = Auth.query.first()
        if not auth_record:
            # 首次运行，设置登录密码
            auth_record = Auth(password_hash=simple_hash(password))
            db.session.add(auth_record)
            db.session.commit()
            session['entry_authenticated'] = True
            return jsonify({'success': True, 'message': '已设置登录密码'})

        if simple_hash(password) == auth_record.password_hash:
            session['entry_authenticated'] = True
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '密码错误'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.json
        password = data.get('password', '')

        auth_record = Auth.query.first()
        if not auth_record:
            auth_record = Auth(admin_password_hash=simple_hash(password))
            db.session.add(auth_record)
            db.session.commit()
            session['admin_authenticated'] = True
            return jsonify({'success': True, 'message': '已设置管理员密码'})

        if not auth_record.admin_password_hash:
            auth_record.admin_password_hash = simple_hash(password)
            db.session.commit()
            session['admin_authenticated'] = True
            return jsonify({'success': True, 'message': '已设置管理员密码'})

        if simple_hash(password) == auth_record.admin_password_hash:
            session['admin_authenticated'] = True
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '密码错误'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    target = request.args.get('type', 'entry')
    if target == 'admin':
        session.pop('admin_authenticated', None)
    else:
        session.pop('entry_authenticated', None)
    return jsonify({'success': True, 'message': '登出成功'})

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查认证状态"""
    target = request.args.get('type', 'entry')
    if target == 'admin':
        authenticated = session.get('admin_authenticated', False)
    else:
        authenticated = session.get('entry_authenticated', False)
    return jsonify({'authenticated': authenticated})

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        target = request.json.get('type', 'entry')

        # 修改密码需要管理员权限
        if not session.get('admin_authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401

        data = request.json
        new_password = data.get('new_password', '')

        if len(new_password) < 1 or len(new_password) > 4:
            return jsonify({'success': False, 'message': '密码长度必须为1-4位'}), 400

        auth_record = Auth.query.first()
        if not auth_record:
            auth_record = Auth()
            db.session.add(auth_record)

        if target == 'admin':
            auth_record.admin_password_hash = simple_hash(new_password)
        else:
            auth_record.password_hash = simple_hash(new_password)

        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

