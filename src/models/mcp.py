from datetime import datetime
from src.models.user import db

class MCPServer(db.Model):
    """MCP服务器配置模型"""
    __tablename__ = 'mcp_servers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    command = db.Column(db.String(200), nullable=False)
    args = db.Column(db.JSON, default=list)  # 存储参数列表
    env = db.Column(db.JSON, default=dict)   # 存储环境变量
    enabled = db.Column(db.Boolean, default=True)
    builtin = db.Column(db.Boolean, default=False)  # 是否为内置服务器
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'args': self.args or [],
            'env': self.env or {},
            'enabled': self.enabled,
            'builtin': self.builtin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserMemory(db.Model):
    """用户记忆模型"""
    __tablename__ = 'user_memories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth.id'), nullable=False)
    memory_type = db.Column(db.String(50), nullable=False)  # preference, habit, fact, etc.
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=1.0)  # 置信度 0-1
    source = db.Column(db.String(100), default='ai_analysis')  # 记忆来源
    tags = db.Column(db.JSON, default=list)  # 标签
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 添加复合索引提高查询性能
    __table_args__ = (
        db.Index('idx_user_memory_type', 'user_id', 'memory_type'),
        db.Index('idx_user_key', 'user_id', 'key'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'memory_type': self.memory_type,
            'key': self.key,
            'value': self.value,
            'confidence': self.confidence,
            'source': self.source,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MCPExecutionLog(db.Model):
    """MCP执行日志模型"""
    __tablename__ = 'mcp_execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(100), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth.id'))
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    execution_time = db.Column(db.Float)  # 执行时间(秒)
    status = db.Column(db.String(20), default='success')  # success, error
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'server_name': self.server_name,
            'tool_name': self.tool_name,
            'user_id': self.user_id,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_time': self.execution_time,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }