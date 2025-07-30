from flask import Blueprint, jsonify, request, session
from src.services.mcp_service import mcp_service

mcp_bp = Blueprint('mcp', __name__)

def require_auth(f):
    """认证装饰器"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@mcp_bp.route('/servers', methods=['GET'])
@require_auth
def get_servers():
    """获取MCP服务器配置"""
    try:
        config = mcp_service.get_server_config()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/config', methods=['POST'])
@require_auth
def update_servers_config():
    """更新MCP服务器配置"""
    try:
        config = request.json
        if not config:
            return jsonify({'success': False, 'message': '无效的配置数据'}), 400
        
        success = mcp_service.update_server_config(config)
        if success:
            return jsonify({
                'success': True,
                'message': 'MCP配置更新成功',
                'config': mcp_service.get_server_config()
            })
        else:
            return jsonify({'success': False, 'message': 'MCP配置更新失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/tools/call', methods=['POST'])
@require_auth
def call_tool():
    """调用MCP工具"""
    try:
        data = request.json
        server_name = data.get('server')
        tool_name = data.get('tool')
        parameters = data.get('parameters', {})
        
        if not server_name or not tool_name:
            return jsonify({'success': False, 'message': '缺少服务器名称或工具名称'}), 400
        
        result = mcp_service.call_tool(server_name, tool_name, parameters)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/resources/<path:uri>', methods=['GET'])
@require_auth
def get_resource(uri):
    """获取MCP资源"""
    try:
        # 重新构建完整的URI
        full_uri = uri
        if not '://' in full_uri:
            # 如果没有协议，从查询参数中获取
            scheme = request.args.get('scheme', 'time')
            full_uri = f"{scheme}://{uri}"
        
        result = mcp_service.get_resource(full_uri)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/context', methods=['GET'])
@require_auth
def get_context():
    """获取AI分析的上下文信息"""
    try:
        entry_text = request.args.get('text')
        image_path = request.args.get('image_path')
        
        context = mcp_service.get_context_for_ai(entry_text, image_path)
        
        return jsonify({
            'success': True,
            'context': context
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/permission/location', methods=['POST'])
@require_auth
def request_location_permission():
    """请求位置权限"""
    try:
        data = request.json
        granted = data.get('granted', False)
        
        # 更新位置权限
        mcp_service.update_server_config({'location_permission': granted})
        
        return jsonify({
            'success': True,
            'message': '位置权限已更新',
            'granted': granted
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/test', methods=['POST'])
@require_auth
def test_mcp():
    """测试MCP功能"""
    try:
        data = request.json
        server_name = data.get('server', 'time')
        
        # 测试不同服务器的基本功能
        if server_name == 'time':
            result = mcp_service.call_tool('time', 'getCurrentTime')
        elif server_name == 'location':
            result = mcp_service.call_tool('location', 'getCurrentLocation')
        elif server_name == 'weather':
            result = mcp_service.call_tool('weather', 'getWeather')
        elif server_name == 'system':
            result = mcp_service.call_tool('system', 'getDeviceInfo')
        else:
            return jsonify({'success': False, 'message': f'未知服务器: {server_name}'}), 400
        
        return jsonify({
            'success': True,
            'message': f'{server_name}服务器测试完成',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

