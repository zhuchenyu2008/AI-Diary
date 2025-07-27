from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DailyDiary(Base):
    __tablename__ = "daily_diaries"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diary_date = Column(Date, nullable=False)
    content_origin = Column(Text, nullable=False)
    content_final = Column(Text, nullable=True)
    pushed_at = Column(DateTime(timezone=True), nullable=True, comment="推送时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 唯一约束：每个用户每天只能有一篇日记
    __table_args__ = (
        UniqueConstraint('user_id', 'diary_date', name='uk_user_date'),
    )
    
    # 关系
    user = relationship("User", backref="diaries")
    
    def __repr__(self):
        return f"<DailyDiary(id={self.id}, user_id={self.user_id}, date={self.diary_date})>" 