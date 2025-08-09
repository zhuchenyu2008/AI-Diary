"""输入验证工具"""
import re
from flask import jsonify

def validate_date_format(date_string):
    """验证日期格式 YYYY-MM-DD"""
    if not date_string or not isinstance(date_string, str):
        return False
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_string))

def validate_pagination(page, per_page, max_per_page=100):
    """验证分页参数"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
        
        if page < 1:
            page = 1
        if per_page < 1 or per_page > max_per_page:
            per_page = min(max_per_page, max(1, per_page))
            
        return page, per_page
    except (ValueError, TypeError):
        return 1, 20

def validate_password_format(password):
    """验证密码格式：1-4位数字"""
    if not password or not isinstance(password, str):
        return False
    return password.isdigit() and 1 <= len(password) <= 4

def sanitize_text_input(text, max_length=10000):
    """清理文本输入"""
    if not text or not isinstance(text, str):
        return ""
    return text.strip()[:max_length]