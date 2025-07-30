import json
import subprocess
import asyncio
import aiohttp
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from src.models.mcp import MCPServer, MCPTool, MCPResource, MCPPrompt, MCPExecution
from src.models.diary import db

class MCPService:
    """MCP服务管理器"""
    
    def __init__(self):
        self.active_connections = {}  # server_id -> connection
        self.server_processes = {}    # server_id -> process
        
    async def start_server(self, server_id: int) -> Tuple[bool, str]:
        """启动MCP服务器"""
        try:
            server = MCPServer.query.get(server_id)
            if not server:
                return False, "服务器不存在"
            
            if not server.enabled:
                return False, "服务器已禁用"
            
            if server.transport == 'stdio':
                return await self._start_stdio_server(server)
            elif server.transport == 'http':
                return await self._start_http_server(server)
            else:
                return False, f"不支持的传输类型: {server.transport}"
                
        except Exception as e:
            return False, f"启动服务器失败: {str(e)}"
    
    async def _start_stdio_server(self, server: MCPServer) -> Tuple[bool, str]:
        """启动STDIO传输的MCP服务器"""
        try:
            if not server.command:
                return False, "未配置启动命令"
            
            # 构建命令和参数
            cmd = [server.command]
            if server.args:
                if isinstance(server.args, list):
                    cmd.extend(server.args)
                elif isinstance(server.args, str):
                    # 如果是字符串，尝试解析为JSON数组
                    try:
                        args_list = json.loads(server.args)
                        if isinstance(args_list, list):
                            cmd.extend(args_list)
                        else:
                            cmd.append(server.args)
                    except json.JSONDecodeError:
                        # 如果不是JSON，按空格分割
                        cmd.extend(server.args.split())
            
            # 设置环境变量
            env = dict(os.environ)
            if server.env_vars:
                if isinstance(server.env_vars, dict):
                    env.update(server.env_vars)
                elif isinstance(server.env_vars, str):
                    try:
                        env_dict = json.loads(server.env_vars)
                        if isinstance(env_dict, dict):
                            env.update(env_dict)
                    except json.JSONDecodeError:
                        pass
            
            # 启动进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.server_processes[server.id] = process
            
            # 等待进程启动
            await asyncio.sleep(1)
            
            # 检查进程是否还在运行
            if process.returncode is not None:
                stderr_output = await process.stderr.read()
                error_msg = stderr_output.decode() if stderr_output else "进程启动后立即退出"
                return False, f"服务器启动失败: {error_msg}"
            
            # 初始化连接
            success = await self._initialize_connection(server.id, process)
            if success:
                server.last_connected = datetime.utcnow()
                db.session.commit()
                return True, "STDIO服务器启动成功"
            else:
                await self._stop_server(server.id)
                return False, "服务器初始化失败"
                
        except Exception as e:
            return False, f"启动STDIO服务器失败: {str(e)}"
    
    async def _start_http_server(self, server: MCPServer) -> Tuple[bool, str]:
        """启动HTTP传输的MCP服务器连接"""
        try:
            if not server.url:
                return False, "未配置服务器URL"
            
            # 创建HTTP会话
            headers = server.headers or {}
            headers['Content-Type'] = 'application/json'
            
            session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=server.timeout)
            )
            
            # 测试连接
            test_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "AI-Diary",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(server.url, json=test_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('result'):
                        self.active_connections[server.id] = session
                        server.last_connected = datetime.utcnow()
                        db.session.commit()
                        return True, "HTTP服务器连接成功"
                    else:
                        await session.close()
                        return False, f"服务器初始化失败: {result.get('error', '未知错误')}"
                else:
                    await session.close()
                    return False, f"HTTP连接失败: {response.status}"
                    
        except Exception as e:
            return False, f"启动HTTP服务器失败: {str(e)}"
    
    async def _initialize_connection(self, server_id: int, process) -> bool:
        """初始化MCP连接"""
        try:
            # 发送初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "AI-Diary",
                        "version": "1.0.0"
                    }
                }
            }
            
            # 发送请求
            request_data = json.dumps(init_request) + '\n'
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            # 等待响应
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=10.0
            )
            
            if response_line:
                response = json.loads(response_line.decode().strip())
                if response.get('result'):
                    self.active_connections[server_id] = process
                    return True
            
            return False
            
        except Exception as e:
            print(f"初始化连接失败: {e}")
            return False
    
    async def stop_server(self, server_id: int) -> Tuple[bool, str]:
        """停止MCP服务器"""
        return await self._stop_server(server_id)
    
    async def _stop_server(self, server_id: int) -> Tuple[bool, str]:
        """内部停止服务器方法"""
        try:
            # 关闭连接
            if server_id in self.active_connections:
                connection = self.active_connections[server_id]
                if isinstance(connection, aiohttp.ClientSession):
                    await connection.close()
                del self.active_connections[server_id]
            
            # 终止进程
            if server_id in self.server_processes:
                process = self.server_processes[server_id]
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                del self.server_processes[server_id]
            
            return True, "服务器已停止"
            
        except Exception as e:
            return False, f"停止服务器失败: {str(e)}"
    
    async def list_tools(self, server_id: int) -> Tuple[bool, List[Dict], str]:
        """列出服务器的工具"""
        try:
            if server_id not in self.active_connections:
                return False, [], "服务器未连接"
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/list"
            }
            
            response = await self._send_request(server_id, request)
            if response and response.get('result'):
                tools = response['result'].get('tools', [])
                
                # 更新数据库中的工具信息
                await self._update_tools_in_db(server_id, tools)
                
                return True, tools, "获取工具列表成功"
            else:
                error_msg = response.get('error', {}).get('message', '未知错误') if response else '无响应'
                return False, [], f"获取工具列表失败: {error_msg}"
                
        except Exception as e:
            return False, [], f"获取工具列表失败: {str(e)}"
    
    async def call_tool(self, server_id: int, tool_name: str, arguments: Dict) -> Tuple[bool, Any, str]:
        """调用工具"""
        try:
            start_time = time.time()
            
            if server_id not in self.active_connections:
                return False, None, "服务器未连接"
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self._send_request(server_id, request)
            execution_time = int((time.time() - start_time) * 1000)
            
            if response and response.get('result'):
                result = response['result']
                
                # 记录执行
                await self._record_execution(
                    server_id, 'tool', tool_name, arguments, 
                    result, 'success', None, execution_time
                )
                
                return True, result, "工具调用成功"
            else:
                error_msg = response.get('error', {}).get('message', '未知错误') if response else '无响应'
                
                # 记录执行失败
                await self._record_execution(
                    server_id, 'tool', tool_name, arguments, 
                    None, 'error', error_msg, execution_time
                )
                
                return False, None, f"工具调用失败: {error_msg}"
                
        except Exception as e:
            return False, None, f"工具调用失败: {str(e)}"
    
    async def list_resources(self, server_id: int) -> Tuple[bool, List[Dict], str]:
        """列出服务器的资源"""
        try:
            if server_id not in self.active_connections:
                return False, [], "服务器未连接"
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "resources/list"
            }
            
            response = await self._send_request(server_id, request)
            if response and response.get('result'):
                resources = response['result'].get('resources', [])
                
                # 更新数据库中的资源信息
                await self._update_resources_in_db(server_id, resources)
                
                return True, resources, "获取资源列表成功"
            else:
                error_msg = response.get('error', {}).get('message', '未知错误') if response else '无响应'
                return False, [], f"获取资源列表失败: {error_msg}"
                
        except Exception as e:
            return False, [], f"获取资源列表失败: {str(e)}"
    
    async def read_resource(self, server_id: int, uri: str) -> Tuple[bool, Any, str]:
        """读取资源"""
        try:
            start_time = time.time()
            
            if server_id not in self.active_connections:
                return False, None, "服务器未连接"
            
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "resources/read",
                "params": {
                    "uri": uri
                }
            }
            
            response = await self._send_request(server_id, request)
            execution_time = int((time.time() - start_time) * 1000)
            
            if response and response.get('result'):
                result = response['result']
                
                # 记录执行
                await self._record_execution(
                    server_id, 'resource', uri, {'uri': uri}, 
                    result, 'success', None, execution_time
                )
                
                return True, result, "资源读取成功"
            else:
                error_msg = response.get('error', {}).get('message', '未知错误') if response else '无响应'
                
                # 记录执行失败
                await self._record_execution(
                    server_id, 'resource', uri, {'uri': uri}, 
                    None, 'error', error_msg, execution_time
                )
                
                return False, None, f"资源读取失败: {error_msg}"
                
        except Exception as e:
            return False, None, f"资源读取失败: {str(e)}"
    
    async def _send_request(self, server_id: int, request: Dict) -> Optional[Dict]:
        """发送请求到MCP服务器"""
        try:
            connection = self.active_connections.get(server_id)
            if not connection:
                return None
            
            if isinstance(connection, aiohttp.ClientSession):
                # HTTP传输
                server = MCPServer.query.get(server_id)
                async with connection.post(server.url, json=request) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            else:
                # STDIO传输
                request_data = json.dumps(request) + '\n'
                connection.stdin.write(request_data.encode())
                await connection.stdin.drain()
                
                response_line = await asyncio.wait_for(
                    connection.stdout.readline(), 
                    timeout=30.0
                )
                
                if response_line:
                    return json.loads(response_line.decode().strip())
                return None
                
        except Exception as e:
            print(f"发送请求失败: {e}")
            return None
    
    async def _update_tools_in_db(self, server_id: int, tools: List[Dict]):
        """更新数据库中的工具信息"""
        try:
            # 删除旧的工具记录
            MCPTool.query.filter_by(server_id=server_id).delete()
            
            # 添加新的工具记录
            for tool in tools:
                mcp_tool = MCPTool(
                    server_id=server_id,
                    name=tool.get('name'),
                    description=tool.get('description'),
                    input_schema=tool.get('inputSchema')
                )
                db.session.add(mcp_tool)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"更新工具信息失败: {e}")
    
    async def _update_resources_in_db(self, server_id: int, resources: List[Dict]):
        """更新数据库中的资源信息"""
        try:
            # 删除旧的资源记录
            MCPResource.query.filter_by(server_id=server_id).delete()
            
            # 添加新的资源记录
            for resource in resources:
                mcp_resource = MCPResource(
                    server_id=server_id,
                    uri=resource.get('uri'),
                    name=resource.get('name'),
                    description=resource.get('description'),
                    mime_type=resource.get('mimeType')
                )
                db.session.add(mcp_resource)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"更新资源信息失败: {e}")
    
    async def _record_execution(self, server_id: int, execution_type: str, 
                              target_name: str, input_data: Dict, output_data: Any, 
                              status: str, error_message: str, execution_time: int):
        """记录执行历史"""
        try:
            execution = MCPExecution(
                server_id=server_id,
                execution_type=execution_type,
                target_name=target_name,
                input_data=input_data,
                output_data=output_data,
                status=status,
                error_message=error_message,
                execution_time=execution_time
            )
            db.session.add(execution)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"记录执行历史失败: {e}")
    
    def get_server_status(self, server_id: int) -> Dict:
        """获取服务器状态"""
        return {
            'connected': server_id in self.active_connections,
            'process_running': server_id in self.server_processes
        }
    
    async def shutdown_all(self):
        """关闭所有连接"""
        for server_id in list(self.active_connections.keys()):
            await self._stop_server(server_id)

# 全局MCP服务实例
mcp_service = MCPService()

