import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.models.mcp import UserMemory, MCPExecutionLog
from src.models.user import db

logger = logging.getLogger(__name__)

class BuiltinUserMCP:
    """内置用户记忆MCP服务器实现"""
    
    def __init__(self, db_session=None):
        self.db = db_session or db.session
        self.server_name = "usermcp"
        
    async def query_user_profile(self, query: str, user_id: int = None) -> Dict[str, Any]:
        """查询用户档案
        
        Args:
            query: 查询内容，可以是关键词、上下文等
            user_id: 用户ID
            
        Returns:
            Dict containing user profile information
        """
        start_time = datetime.now()
        try:
            if not user_id:
                return {"error": "用户ID为空"}
            
            # 简单的关键词匹配查询
            memories = UserMemory.query.filter(
                UserMemory.user_id == user_id,
                db.or_(
                    UserMemory.key.contains(query),
                    UserMemory.value.contains(query)
                )
            ).order_by(UserMemory.confidence.desc()).limit(10).all()
            
            result = {
                "user_id": user_id,
                "query": query,
                "memories": []
            }
            
            for memory in memories:
                result["memories"].append({
                    "type": memory.memory_type,
                    "key": memory.key,
                    "value": memory.value,
                    "confidence": memory.confidence,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat()
                })
            
            # 记录执行日志
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_execution("usermcp_query_user_profile", user_id, 
                              {"query": query}, result, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"查询用户档案失败: {error_msg}")
            
            self._log_execution("usermcp_query_user_profile", user_id,
                              {"query": query}, None, execution_time, 
                              "error", error_msg)
            
            return {"error": error_msg}
    
    async def insert_user_profile(self, key: str, value: str, user_id: int = None, 
                                 memory_type: str = "preference", confidence: float = 1.0,
                                 tags: List[str] = None) -> Dict[str, Any]:
        """插入用户档案
        
        Args:
            key: 记忆关键词
            value: 记忆内容
            user_id: 用户ID
            memory_type: 记忆类型
            confidence: 置信度
            tags: 标签列表
            
        Returns:
            Dict containing operation result
        """
        start_time = datetime.now()
        try:
            if not user_id:
                return {"error": "用户ID为空"}
            
            if not key or not value:
                return {"error": "关键词或内容为空"}
            
            # 检查是否已存在相同的记忆
            existing = UserMemory.query.filter(
                UserMemory.user_id == user_id,
                UserMemory.key == key,
                UserMemory.memory_type == memory_type
            ).first()
            
            if existing:
                # 更新现有记忆
                existing.value = value
                existing.confidence = max(existing.confidence, confidence)
                existing.tags = list(set((existing.tags or []) + (tags or [])))
                existing.updated_at = datetime.utcnow()
                operation = "updated"
                memory_id = existing.id
            else:
                # 创建新记忆
                memory = UserMemory(
                    user_id=user_id,
                    memory_type=memory_type,
                    key=key,
                    value=value,
                    confidence=confidence,
                    source='ai_analysis',
                    tags=tags or []
                )
                self.db.add(memory)
                self.db.flush()  # 获取ID但不提交
                memory_id = memory.id
                operation = "created"
            
            self.db.commit()
            
            result = {
                "operation": operation,
                "memory_id": memory_id,
                "key": key,
                "value": value,
                "confidence": confidence
            }
            
            # 记录执行日志
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_execution("usermcp_insert_user_profile", user_id,
                              {"key": key, "value": value, "memory_type": memory_type},
                              result, execution_time)
            
            return result
            
        except Exception as e:
            self.db.rollback()
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"插入用户档案失败: {error_msg}")
            
            self._log_execution("usermcp_insert_user_profile", user_id,
                              {"key": key, "value": value}, None,
                              execution_time, "error", error_msg)
            
            return {"error": error_msg}
    
    async def delete_user_profile(self, key: str, user_id: int = None, 
                                 memory_type: str = None) -> Dict[str, Any]:
        """删除用户档案
        
        Args:
            key: 记忆关键词
            user_id: 用户ID
            memory_type: 记忆类型（可选，不指定则删除所有匹配的）
            
        Returns:
            Dict containing operation result
        """
        start_time = datetime.now()
        try:
            if not user_id:
                return {"error": "用户ID为空"}
            
            if not key:
                return {"error": "关键词为空"}
            
            # 构建查询条件
            query = UserMemory.query.filter(
                UserMemory.user_id == user_id,
                UserMemory.key == key
            )
            
            if memory_type:
                query = query.filter(UserMemory.memory_type == memory_type)
            
            memories = query.all()
            deleted_count = len(memories)
            
            if deleted_count == 0:
                return {"message": "未找到匹配的记忆", "deleted_count": 0}
            
            # 删除记忆
            for memory in memories:
                self.db.delete(memory)
            
            self.db.commit()
            
            result = {
                "message": f"成功删除 {deleted_count} 条记忆",
                "deleted_count": deleted_count,
                "key": key
            }
            
            # 记录执行日志
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_execution("usermcp_delete_user_profile", user_id,
                              {"key": key, "memory_type": memory_type},
                              result, execution_time)
            
            return result
            
        except Exception as e:
            self.db.rollback()
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"删除用户档案失败: {error_msg}")
            
            self._log_execution("usermcp_delete_user_profile", user_id,
                              {"key": key}, None, execution_time, "error", error_msg)
            
            return {"error": error_msg}
    
    def get_user_memory_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户记忆统计信息"""
        try:
            total_count = UserMemory.query.filter(UserMemory.user_id == user_id).count()
            
            # 按类型统计
            from sqlalchemy import func
            type_stats = db.session.query(
                UserMemory.memory_type,
                func.count(UserMemory.id).label('count')
            ).filter(UserMemory.user_id == user_id).group_by(UserMemory.memory_type).all()
            
            # 最近记忆
            recent_memories = UserMemory.query.filter(
                UserMemory.user_id == user_id
            ).order_by(UserMemory.updated_at.desc()).limit(5).all()
            
            return {
                "total_count": total_count,
                "type_stats": [{"type": stat.memory_type, "count": stat.count} for stat in type_stats],
                "recent_memories": [memory.to_dict() for memory in recent_memories]
            }
            
        except Exception as e:
            logger.error(f"获取用户记忆统计失败: {e}")
            return {"error": str(e)}
    
    def _log_execution(self, tool_name: str, user_id: int, input_data: Dict,
                      output_data: Dict, execution_time: float,
                      status: str = "success", error_message: str = None):
        """记录执行日志"""
        try:
            log = MCPExecutionLog(
                server_name=self.server_name,
                tool_name=tool_name,
                user_id=user_id,
                input_data=input_data,
                output_data=output_data,
                execution_time=execution_time,
                status=status,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            logger.error(f"记录执行日志失败: {e}")
            self.db.rollback()