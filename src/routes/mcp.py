from flask import Blueprint, jsonify, request, session
from src.models.mcp import MCPServer, MCPTool, MCPResource, MCPPrompt, MCPExecution
from src.models.diary import db
from src.services.mcp_service import mcp_service
import asyncio
import json

mcp_bp = Blueprint('mcp', __name__)

def require_auth(f):
    """认证装饰器"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated', False):
            return jsonify({'success': False, 'message': '未认证'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def run_async(coro):
    """运行异步函数的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@mcp_bp.route('/servers', methods=['GET'])
@require_auth
def get_servers():
    """获取所有MCP服务器"""
    try:
        servers = MCPServer.query.all()
        servers_data = []
        
        for server in servers:
            server_data = server.to_dict()
            # 添加状态信息
            status = mcp_service.get_server_status(server.id)
            server_data['status'] = status
            servers_data.append(server_data)
        
        return jsonify({
            'success': True,
            'servers': servers_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers', methods=['POST'])
@require_auth
def create_server():
    """创建MCP服务器"""
    try:
        data = request.json
        
        # 处理用户自定义的MCP服务器配置格式
        if 'mcpServers' in data:
            # 用户提供的是标准MCP配置格式
            mcp_servers = data['mcpServers']
            created_servers = []
            
            for server_name, server_config in mcp_servers.items():
                # 检查名称是否已存在
                existing = MCPServer.query.filter_by(name=server_name).first()
                if existing:
                    return jsonify({'success': False, 'message': f'服务器名称 {server_name} 已存在'}), 400
                
                # 创建服务器
                server = MCPServer(
                    name=server_name,
                    description=server_config.get('description', f'MCP服务器: {server_name}'),
                    server_type='local',  # 默认为本地服务器
                    transport='stdio',    # 默认为stdio传输
                    command=server_config.get('command'),
                    args=server_config.get('args', []),
                    enabled=True,
                    auto_start=True,
                    timeout=30
                )
                
                db.session.add(server)
                created_servers.append(server)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'成功创建 {len(created_servers)} 个服务器',
                'servers': [server.to_dict() for server in created_servers]
            })
        
        else:
            # 原有的单个服务器创建逻辑
            # 验证必需字段 - 移除server_type要求
            required_fields = ['name', 'transport']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'message': f'缺少必需字段: {field}'}), 400
            
            # 检查名称是否已存在
            existing = MCPServer.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'success': False, 'message': '服务器名称已存在'}), 400
            
            # 创建服务器 - server_type设为默认值
            server = MCPServer(
                name=data['name'],
                description=data.get('description', ''),
                server_type=data.get('server_type', 'local'),  # 默认为local
                transport=data['transport'],
                command=data.get('command'),
                args=data.get('args'),
                url=data.get('url'),
                headers=data.get('headers'),
                enabled=data.get('enabled', True),
                auto_start=data.get('auto_start', True),
                timeout=data.get('timeout', 30)
            )
            
            db.session.add(server)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '服务器创建成功',
                'server': server.to_dict()
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>', methods=['PUT'])
@require_auth
def update_server(server_id):
    """更新MCP服务器"""
    try:
        server = MCPServer.query.get_or_404(server_id)
        data = request.json
        
        # 更新字段
        for field in ['name', 'description', 'server_type', 'transport', 
                     'command', 'args', 'url', 'headers', 'enabled', 
                     'auto_start', 'timeout']:
            if field in data:
                setattr(server, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '服务器更新成功',
            'server': server.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>', methods=['DELETE'])
@require_auth
def delete_server(server_id):
    """删除MCP服务器"""
    try:
        server = MCPServer.query.get_or_404(server_id)
        
        # 停止服务器
        run_async(mcp_service.stop_server(server_id))
        
        # 删除相关记录
        MCPTool.query.filter_by(server_id=server_id).delete()
        MCPResource.query.filter_by(server_id=server_id).delete()
        MCPPrompt.query.filter_by(server_id=server_id).delete()
        MCPExecution.query.filter_by(server_id=server_id).delete()
        
        db.session.delete(server)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '服务器删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/start', methods=['POST'])
@require_auth
def start_server(server_id):
    """启动MCP服务器"""
    try:
        success, message = run_async(mcp_service.start_server(server_id))
        
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
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/stop', methods=['POST'])
@require_auth
def stop_server(server_id):
    """停止MCP服务器"""
    try:
        success, message = run_async(mcp_service.stop_server(server_id))
        
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
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/tools', methods=['GET'])
@require_auth
def get_tools(server_id):
    """获取服务器工具列表"""
    try:
        success, tools, message = run_async(mcp_service.list_tools(server_id))
        
        if success:
            return jsonify({
                'success': True,
                'tools': tools,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/tools/<string:tool_name>/call', methods=['POST'])
@require_auth
def call_tool(server_id, tool_name):
    """调用工具"""
    try:
        data = request.json
        arguments = data.get('arguments', {})
        
        success, result, message = run_async(
            mcp_service.call_tool(server_id, tool_name, arguments)
        )
        
        if success:
            return jsonify({
                'success': True,
                'result': result,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/resources', methods=['GET'])
@require_auth
def get_resources(server_id):
    """获取服务器资源列表"""
    try:
        success, resources, message = run_async(mcp_service.list_resources(server_id))
        
        if success:
            return jsonify({
                'success': True,
                'resources': resources,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/<int:server_id>/resources/read', methods=['POST'])
@require_auth
def read_resource(server_id):
    """读取资源"""
    try:
        data = request.json
        uri = data.get('uri')
        
        if not uri:
            return jsonify({'success': False, 'message': '缺少URI参数'}), 400
        
        success, result, message = run_async(
            mcp_service.read_resource(server_id, uri)
        )
        
        if success:
            return jsonify({
                'success': True,
                'result': result,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/executions', methods=['GET'])
@require_auth
def get_executions():
    """获取执行历史"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        server_id = request.args.get('server_id', type=int)
        
        query = MCPExecution.query
        if server_id:
            query = query.filter_by(server_id=server_id)
        
        executions = query.order_by(MCPExecution.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'executions': [execution.to_dict() for execution in executions.items],
            'pagination': {
                'page': executions.page,
                'pages': executions.pages,
                'per_page': executions.per_page,
                'total': executions.total,
                'has_next': executions.has_next,
                'has_prev': executions.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/builtin-servers', methods=['GET'])
@require_auth
def get_builtin_servers():
    """获取内置MCP服务器模板"""
    try:
        builtin_servers = [
            {
                'name': 'time-server',
                'display_name': '时间服务器',
                'description': '提供当前时间和日期信息',
                'server_type': 'local',
                'transport': 'stdio',
                'command': 'python',
                'args': ['-m', 'mcp_time_server'],
                'capabilities': ['tools'],
                'tools': [
                    {
                        'name': 'get_current_time',
                        'description': '获取当前时间'
                    },
                    {
                        'name': 'get_timezone_info',
                        'description': '获取时区信息'
                    }
                ]
            },
            {
                'name': 'location-server',
                'display_name': '位置服务器',
                'description': '提供用户位置信息（需要浏览器权限）',
                'server_type': 'local',
                'transport': 'stdio',
                'command': 'python',
                'args': ['-m', 'mcp_location_server'],
                'capabilities': ['tools', 'resources'],
                'tools': [
                    {
                        'name': 'get_current_location',
                        'description': '获取当前位置'
                    },
                    {
                        'name': 'get_weather_by_location',
                        'description': '根据位置获取天气信息'
                    }
                ]
            },
            {
                'name': 'web-search-server',
                'display_name': '网络搜索服务器',
                'description': '提供网络搜索功能',
                'server_type': 'remote',
                'transport': 'http',
                'url': 'https://api.example.com/mcp',
                'capabilities': ['tools'],
                'tools': [
                    {
                        'name': 'search_web',
                        'description': '搜索网络内容'
                    },
                    {
                        'name': 'get_page_content',
                        'description': '获取网页内容'
                    }
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'servers': builtin_servers
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/servers/create-from-template', methods=['POST'])
@require_auth
def create_server_from_template():
    """从模板创建MCP服务器"""
    try:
        data = request.json
        template_name = data.get('template_name')
        custom_name = data.get('custom_name')
        
        if not template_name or not custom_name:
            return jsonify({'success': False, 'message': '缺少必需参数'}), 400
        
        # 获取内置服务器模板
        builtin_servers = {
            'time-server': {
                'description': '提供当前时间和日期信息',
                'server_type': 'local',
                'transport': 'stdio',
                'command': 'python',
                'args': ['-m', 'mcp_time_server']
            },
            'location-server': {
                'description': '提供用户位置信息（需要浏览器权限）',
                'server_type': 'local',
                'transport': 'stdio',
                'command': 'python',
                'args': ['-m', 'mcp_location_server']
            },
            'web-search-server': {
                'description': '提供网络搜索功能',
                'server_type': 'remote',
                'transport': 'http',
                'url': 'https://api.example.com/mcp'
            }
        }
        
        template = builtin_servers.get(template_name)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        # 检查名称是否已存在
        existing = MCPServer.query.filter_by(name=custom_name).first()
        if existing:
            return jsonify({'success': False, 'message': '服务器名称已存在'}), 400
        
        # 创建服务器
        server = MCPServer(
            name=custom_name,
            description=template['description'],
            server_type=template['server_type'],
            transport=template['transport'],
            command=template.get('command'),
            args=template.get('args'),
            url=template.get('url'),
            enabled=True,
            auto_start=True
        )
        
        db.session.add(server)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '服务器创建成功',
            'server': server.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

