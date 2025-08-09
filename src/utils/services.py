"""应用工厂和服务管理器"""
import logging
from flask import Flask

logger = logging.getLogger(__name__)

class ServiceManager:
    """服务管理器 - 避免全局单例"""
    
    def __init__(self, app=None):
        self.app = app
        self._ai_service = None
        self._telegram_service = None
        self._scheduler_service = None
        self._mcp_manager = None
        
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        
    def get_ai_service(self):
        """获取AI服务实例"""
        if self._ai_service is None:
            from src.services.ai_service import AIService
            self._ai_service = AIService()
        return self._ai_service
        
    def get_telegram_service(self):
        """获取Telegram服务实例"""
        if self._telegram_service is None:
            from src.services.telegram_service import TelegramService
            self._telegram_service = TelegramService()
        return self._telegram_service
        
    def get_scheduler_service(self):
        """获取调度服务实例"""
        if self._scheduler_service is None:
            from src.services.scheduler_service import SchedulerService
            self._scheduler_service = SchedulerService()
        return self._scheduler_service
        
    def get_mcp_manager(self, db_session=None):
        """获取MCP管理器实例"""
        if self._mcp_manager is None:
            from src.mcp.client import MCPClientManager
            self._mcp_manager = MCPClientManager(db_session)
        return self._mcp_manager

# 全局服务管理器实例
service_manager = ServiceManager()