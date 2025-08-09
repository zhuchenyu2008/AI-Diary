"""统一API响应格式工具"""

def success_response(message="操作成功", data=None, **kwargs):
    """成功响应格式"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response.update(data)
    response.update(kwargs)
    return response

def error_response(message="操作失败", status_code=400, **kwargs):
    """错误响应格式"""
    response = {
        'success': False,
        'message': message
    }
    response.update(kwargs)
    return response, status_code