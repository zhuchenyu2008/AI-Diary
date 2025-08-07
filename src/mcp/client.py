import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClientManager:
    """MCP客户端管理器"""
    
    def __init__(self, db_session=None):
        self.clients = {}  # server_name -> client_info
        self.db = db_session
        self.builtin_usermcp = None
        
    async def start_server(self, server_config: dict) -> bool:
        """启动MCP服务器并建立连接"""
        try:
            server_name = server_config.get('name')
            command = server_config.get('command')
            args = server_config.get('args', [])
            
            logger.info(f"启动MCP服务器: {server_name}")
            
            # 这里实际应该使用真正的MCP客户端库
            # 暂时用模拟实现
            client_info = {
                'name': server_name,
                'command': command,
                'args': args,
                'status': 'running',
                'started_at': datetime.now()
            }
            
            self.clients[server_name] = client_info
            logger.info(f"MCP服务器 {server_name} 启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动MCP服务器失败: {e}")
            return False
    
    async def stop_server(self, server_name: str) -> bool:
        """停止MCP服务器"""
        try:
            if server_name in self.clients:
                del self.clients[server_name]
                logger.info(f"MCP服务器 {server_name} 已停止")
                return True
            return False
        except Exception as e:
            logger.error(f"停止MCP服务器失败: {e}")
            return False
    
    async def query_user_context(self, user_id: int, context: str) -> Dict[str, Any]:
        """查询用户上下文信息"""
        try:
            if self.builtin_usermcp:
                return await self.builtin_usermcp.query_user_profile(context, user_id)
            return {}
        except Exception as e:
            logger.error(f"查询用户上下文失败: {e}")
            return {}
    
    async def update_user_memory(self, user_id: int, memory_data: Dict[str, Any]) -> bool:
        """更新用户记忆"""
        try:
            if self.builtin_usermcp and memory_data:
                for key, value in memory_data.items():
                    await self.builtin_usermcp.insert_user_profile(key, str(value), user_id)
                return True
            return False
        except Exception as e:
            logger.error(f"更新用户记忆失败: {e}")
            return False
    
    def get_server_status(self) -> List[Dict[str, Any]]:
        """获取所有服务器状态"""
        return [
            {
                'name': info['name'],
                'status': info['status'],
                'started_at': info['started_at'].isoformat() if info.get('started_at') else None,
                'command': info.get('command'),
                'args': info.get('args', [])
            }
            for info in self.clients.values()
        ]
    
    async def initialize_builtin_servers(self):
        """初始化内置服务器"""
        try:
            from .usermcp_builtin import BuiltinUserMCP
            self.builtin_usermcp = BuiltinUserMCP(self.db)
            
            # 添加到客户端列表
            self.clients['usermcp'] = {
                'name': 'usermcp',
                'command': 'builtin',
                'args': [],
                'status': 'running',
                'started_at': datetime.now()
            }
            
            logger.info("内置usermcp服务器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化内置服务器失败: {e}")

# 全局MCP客户端管理器实例
mcp_manager = None

def get_mcp_manager(db_session=None) -> MCPClientManager:
    """获取MCP管理器实例"""
    global mcp_manager
    if mcp_manager is None:
        mcp_manager = MCPClientManager(db_session)
    return mcp_manager