from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from src.models.diary import db

class MCPServer(db.Model):
    """MCP服务器配置模型"""
    __tablename__ = 'mcp_servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    server_type = Column(String(50), nullable=False)  # 'local' or 'remote'
    
    # 连接配置
    transport = Column(String(20), nullable=False)  # 'stdio' or 'http'
    command = Column(String(500))  # 用于stdio传输的命令
    args = Column(JSON)  # 命令参数
    url = Column(String(500))  # 用于HTTP传输的URL
    headers = Column(JSON)  # HTTP头部
    
    # 状态和配置
    enabled = Column(Boolean, default=True)
    auto_start = Column(Boolean, default=True)
    timeout = Column(Integer, default=30)  # 连接超时时间（秒）
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_connected = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'server_type': self.server_type,
            'transport': self.transport,
            'command': self.command,
            'args': self.args,
            'url': self.url,
            'headers': self.headers,
            'enabled': self.enabled,
            'auto_start': self.auto_start,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_connected': self.last_connected.isoformat() if self.last_connected else None
        }

class MCPTool(db.Model):
    """MCP工具模型"""
    __tablename__ = 'mcp_tools'
    
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, db.ForeignKey('mcp_servers.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)  # JSON Schema for input validation
    
    # 状态
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'enabled': self.enabled,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MCPResource(db.Model):
    """MCP资源模型"""
    __tablename__ = 'mcp_resources'
    
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, db.ForeignKey('mcp_servers.id'), nullable=False)
    uri = Column(String(500), nullable=False)
    name = Column(String(100))
    description = Column(Text)
    mime_type = Column(String(100))
    
    # 状态
    enabled = Column(Boolean, default=True)
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'uri': self.uri,
            'name': self.name,
            'description': self.description,
            'mime_type': self.mime_type,
            'enabled': self.enabled,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MCPPrompt(db.Model):
    """MCP提示词模型"""
    __tablename__ = 'mcp_prompts'
    
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, db.ForeignKey('mcp_servers.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    arguments = Column(JSON)  # 提示词参数定义
    
    # 状态
    enabled = Column(Boolean, default=True)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'name': self.name,
            'description': self.description,
            'arguments': self.arguments,
            'enabled': self.enabled,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MCPExecution(db.Model):
    """MCP执行记录模型"""
    __tablename__ = 'mcp_executions'
    
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, db.ForeignKey('mcp_servers.id'), nullable=False)
    execution_type = Column(String(20), nullable=False)  # 'tool', 'resource', 'prompt'
    target_name = Column(String(100), nullable=False)  # 工具/资源/提示词名称
    
    # 执行详情
    input_data = Column(JSON)  # 输入参数
    output_data = Column(JSON)  # 输出结果
    status = Column(String(20), nullable=False)  # 'success', 'error', 'timeout'
    error_message = Column(Text)
    execution_time = Column(Integer)  # 执行时间（毫秒）
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'execution_type': self.execution_type,
            'target_name': self.target_name,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'status': self.status,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

