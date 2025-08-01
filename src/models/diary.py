from src.models.user import db
from datetime import datetime
from src.services.time_service import time_service
import json

class DiaryEntry(db.Model):
    """日记条目模型"""
    __tablename__ = 'diary_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time(), nullable=False)
    text_content = db.Column(db.Text)  # 用户输入的文字内容
    image_path = db.Column(db.String(255))  # 图片存储路径
    ai_analysis = db.Column(db.Text)  # AI分析结果
    created_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time())
    
    def __repr__(self):
        return f'<DiaryEntry {self.id} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'text_content': self.text_content,
            'image_path': self.image_path,
            'ai_analysis': self.ai_analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DailySummary(db.Model):
    """每日汇总模型"""
    __tablename__ = 'daily_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)  # 日期（年-月-日）
    summary_content = db.Column(db.Text, nullable=False)  # AI汇总的日记内容
    entry_count = db.Column(db.Integer, default=0)  # 当日条目数量
    created_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time())
    
    def __repr__(self):
        return f'<DailySummary {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'summary_content': self.summary_content,
            'entry_count': self.entry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Config(db.Model):
    """系统配置模型"""
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time())
    updated_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time(), onupdate=lambda: time_service.get_beijing_time())
    
    def __repr__(self):
        return f'<Config {self.key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Auth(db.Model):
    """认证模型"""
    __tablename__ = 'auth'
    
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)  # 密码哈希
    created_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time())
    updated_at = db.Column(db.DateTime, default=lambda: time_service.get_beijing_time(), onupdate=lambda: time_service.get_beijing_time())
    
    def __repr__(self):
        return f'<Auth {self.id}>'

