from flask import Blueprint, jsonify, request
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户。

    要求用户名和邮箱均非空且唯一，否则返回 400 错误。
    """
    data = request.json or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()

    # 校验输入
    if not username or not email:
        return jsonify({'success': False, 'message': '用户名和邮箱不能为空'}), 400

    # 检查用户是否已存在
    existing_user_by_name = User.query.filter_by(username=username).first()
    if existing_user_by_name:
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    existing_user_by_email = User.query.filter_by(email=email).first()
    if existing_user_by_email:
        return jsonify({'success': False, 'message': '邮箱已存在'}), 400

    # 创建新用户
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
