from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Moment(Base):
    __tablename__ = "moments"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(1024), nullable=True)
    user_text = Column(Text, nullable=True)
    ai_description_origin = Column(Text, nullable=True, comment="AI原始分析")
    ai_description_final = Column(Text, nullable=True, comment="人工/规则修饰后文案")
    image_verified = Column(Boolean, default=False, comment="图片校验/压缩标记")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="moments")
    
    def __repr__(self):
        return f"<Moment(id={self.id}, user_id={self.user_id}, has_image={bool(self.image_url)})>" 