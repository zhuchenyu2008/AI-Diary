from flask import Blueprint, request, jsonify, session
from src.models.mcp import MCPServer, UserMemory, MCPExecutionLog
from src.models.user import db
from src.mcp.client import get_mcp_manager
import json
import asyncio

mcp_bp = Blueprint('mcp', __name__)

def require_auth(f):
    """认证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '未授权'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@mcp_bp.route('/mcp/servers', methods=['GET'])
@require_auth
def get_servers():
    """获取MCP服务器列表"""
    try:
        servers = MCPServer.query.all()
        mcp_manager = get_mcp_manager(db.session)
        server_status = mcp_manager.get_server_status()
        
        # 创建状态映射
        status_map = {s['name']: s for s in server_status}
        
        result = []
        for server in servers:
            server_dict = server.to_dict()
            if server.name in status_map:
                server_dict['status'] = status_map[server.name]['status']
            else:
                server_dict['status'] = 'stopped'
            result.append(server_dict)
            
        return jsonify({'servers': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/servers', methods=['POST'])
@require_auth
def create_server():
    """创建MCP服务器配置"""
    try:
        data = request.json
        if not data or not data.get('name') or not data.get('command'):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 检查名称是否已存在
        existing = MCPServer.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': '服务器名称已存在'}), 400
        
        server = MCPServer(
            name=data['name'],
            command=data['command'],
            args=data.get('args', []),
            env=data.get('env', {}),
            enabled=data.get('enabled', True),
            builtin=False
        )
        
        db.session.add(server)
        db.session.commit()
        
        return jsonify({'message': '服务器配置创建成功', 'server': server.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/servers/<int:server_id>', methods=['PUT'])
@require_auth
def update_server(server_id):
    """更新MCP服务器配置"""
    try:
        server = MCPServer.query.get_or_404(server_id)
        data = request.json
        
        if data.get('name') and data['name'] != server.name:
            # 检查新名称是否已存在
            existing = MCPServer.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': '服务器名称已存在'}), 400
            server.name = data['name']
        
        if 'command' in data:
            server.command = data['command']
        if 'args' in data:
            server.args = data['args']
        if 'env' in data:
            server.env = data['env']
        if 'enabled' in data:
            server.enabled = data['enabled']
            
        db.session.commit()
        
        return jsonify({'message': '服务器配置更新成功', 'server': server.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/servers/<int:server_id>', methods=['DELETE'])
@require_auth
def delete_server(server_id):
    """删除MCP服务器配置"""
    try:
        server = MCPServer.query.get_or_404(server_id)
        
        if server.builtin:
            return jsonify({'error': '不能删除内置服务器'}), 400
        
        # 停止服务器（如果正在运行）
        mcp_manager = get_mcp_manager(db.session)
        import asyncio
        asyncio.run(mcp_manager.stop_server(server.name))
        
        db.session.delete(server)
        db.session.commit()
        
        return jsonify({'message': '服务器配置删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/servers/<int:server_id>/toggle', methods=['POST'])
@require_auth
def toggle_server(server_id):
    """启动/停止MCP服务器"""
    try:
        server = MCPServer.query.get_or_404(server_id)
        mcp_manager = get_mcp_manager(db.session)
        
        # 由于Flask路由不支持async，我们需要使用asyncio.run
        import asyncio
        
        if server.enabled:
            # 启动服务器
            success = asyncio.run(mcp_manager.start_server({
                'name': server.name,
                'command': server.command,
                'args': server.args,
                'env': server.env
            }))
            if success:
                return jsonify({'message': f'服务器 {server.name} 启动成功'})
            else:
                return jsonify({'error': f'服务器 {server.name} 启动失败'}), 500
        else:
            # 停止服务器
            success = asyncio.run(mcp_manager.stop_server(server.name))
            if success:
                return jsonify({'message': f'服务器 {server.name} 停止成功'})
            else:
                return jsonify({'error': f'服务器 {server.name} 停止失败'}), 500
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/memories', methods=['GET'])
@require_auth
def get_memories():
    """获取用户记忆列表"""
    try:
        user_id = session['user_id']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        memory_type = request.args.get('type')
        search = request.args.get('search')
        
        query = UserMemory.query.filter(UserMemory.user_id == user_id)
        
        if memory_type:
            query = query.filter(UserMemory.memory_type == memory_type)
        
        if search:
            query = query.filter(db.or_(
                UserMemory.key.contains(search),
                UserMemory.value.contains(search)
            ))
        
        pagination = query.order_by(UserMemory.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        memories = [memory.to_dict() for memory in pagination.items]
        
        return jsonify({
            'memories': memories,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/memories/stats', methods=['GET'])
@require_auth
def get_memory_stats():
    """获取用户记忆统计"""
    try:
        user_id = session['user_id']
        mcp_manager = get_mcp_manager(db.session)
        
        if mcp_manager.builtin_usermcp:
            stats = mcp_manager.builtin_usermcp.get_user_memory_stats(user_id)
            return jsonify(stats)
        else:
            return jsonify({'error': 'usermcp服务未启用'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/memories/<int:memory_id>', methods=['DELETE'])
@require_auth
def delete_memory(memory_id):
    """删除指定记忆"""
    try:
        user_id = session['user_id']
        memory = UserMemory.query.filter(
            UserMemory.id == memory_id,
            UserMemory.user_id == user_id
        ).first_or_404()
        
        db.session.delete(memory)
        db.session.commit()
        
        return jsonify({'message': '记忆删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/memories/batch', methods=['DELETE'])
@require_auth
def delete_memories_batch():
    """批量删除记忆"""
    try:
        user_id = session['user_id']
        data = request.json
        memory_ids = data.get('memory_ids', [])
        
        if not memory_ids:
            return jsonify({'error': '未指定要删除的记忆'}), 400
        
        deleted_count = UserMemory.query.filter(
            UserMemory.id.in_(memory_ids),
            UserMemory.user_id == user_id
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {deleted_count} 条记忆',
            'deleted_count': deleted_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/mcp/logs', methods=['GET'])
@require_auth
def get_execution_logs():
    """获取MCP执行日志"""
    try:
        user_id = session['user_id']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        server_name = request.args.get('server')
        
        query = MCPExecutionLog.query.filter(MCPExecutionLog.user_id == user_id)
        
        if server_name:
            query = query.filter(MCPExecutionLog.server_name == server_name)
        
        pagination = query.order_by(MCPExecutionLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs = [log.to_dict() for log in pagination.items]
        
        return jsonify({
            'logs': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500