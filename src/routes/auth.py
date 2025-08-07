from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.diary import Auth, db
import hashlib

auth_bp = Blueprint('auth', __name__)

# NOTE: Retain a simple MD5 hash helper only for backwards‑compatibility
# with legacy passwords.  New passwords are always generated using
# Werkzeug's secure generate_password_hash.  MD5 is insecure for
# storing passwords and should not be used for new hashes.
def _legacy_md5(password: str) -> str:
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
            # 如果没有设置密码，创建默认密码 "1234"。使用安全哈希。
            default_password_hash = generate_password_hash("1234")
            auth_record = Auth(password_hash=default_password_hash)
            db.session.add(auth_record)
            db.session.commit()

        # 如果存在多条认证记录，只保留第一条，删除其他重复记录
        all_records = Auth.query.all()
        if len(all_records) > 1:
            for extra in all_records[1:]:
                db.session.delete(extra)
            db.session.commit()
        
        # 验证密码：优先使用安全算法校验，如果失败则尝试兼容旧的MD5哈希
        password_correct = False
        try:
            if check_password_hash(auth_record.password_hash, password):
                password_correct = True
        except Exception:
            # 如果存储的不是Werkzeug格式哈希，check_password_hash可能抛出异常
            password_correct = False
        # 回退到MD5比较旧密码
        if not password_correct and _legacy_md5(password) == auth_record.password_hash:
            password_correct = True
        if password_correct:
            session['authenticated'] = True
            session['user_id'] = auth_record.id  # 添加user_id到session
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '密码错误'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.pop('authenticated', None)
    session.pop('user_id', None)  # 同时清除user_id
    return jsonify({'success': True, 'message': '登出成功'})

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """检查认证状态"""
    authenticated = session.get('authenticated', False)
    return jsonify({'authenticated': authenticated})

# 合并密码修改逻辑，保留一个 change‑password 端点。根据是否提供 current_password
# 来决定是否需要验证旧密码。只允许 1‑4 位的数字作为新密码。
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码（可选验证当前密码）"""
    try:
        # 检查是否已认证
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401

        data = request.json or {}
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # 检查新密码
        if not new_password or not isinstance(new_password, str):
            return jsonify({'success': False, 'message': '新密码不能为空'}), 400
        # 仅允许 1‑4 位数字
        if not new_password.isdigit() or len(new_password) < 1 or len(new_password) > 4:
            return jsonify({'success': False, 'message': '新密码必须是1-4位数字'}), 400

        # 检查并清理多余的认证记录
        all_records = Auth.query.all()
        if len(all_records) > 1:
            for extra in all_records[1:]:
                db.session.delete(extra)
            db.session.commit()
        auth_record = all_records[0] if all_records else None

        # 如果不存在认证记录，则直接创建
        if not auth_record:
            hashed = generate_password_hash(new_password)
            auth_record = Auth(password_hash=hashed)
            db.session.add(auth_record)
            db.session.commit()
            return jsonify({'success': True, 'message': '密码设置成功'})

        # 如果存在认证记录，则必须提供 current_password 进行验证
        if not current_password:
            return jsonify({'success': False, 'message': '请提供当前密码'}), 400

        # 校验当前密码：先尝试使用安全哈希，再尝试旧的MD5
        valid_current = False
        try:
            if check_password_hash(auth_record.password_hash, current_password):
                valid_current = True
        except Exception:
            valid_current = False
        if not valid_current and _legacy_md5(current_password) == auth_record.password_hash:
            valid_current = True
        if not valid_current:
            return jsonify({'success': False, 'message': '当前密码错误'}), 400

        # 更新密码为安全哈希
        auth_record.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

