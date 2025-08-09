from flask import session, jsonify
from functools import wraps

def require_auth(f):
    """统一的认证装饰器，要求用户已登录。
    
    使用functools.wraps保留原函数的元数据，便于调试与文档生成。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)
    
    return decorated_function