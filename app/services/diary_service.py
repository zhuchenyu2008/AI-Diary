from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.moment import Moment
from app.models.diary import DailyDiary
from app.services.ai_service import AIService


class DiaryService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_daily_diary(self, user_id: int, diary_date: date, db: Session) -> str:
        """生成指定日期的日记"""
        # 获取当天的所有瞬间
        moments = db.query(Moment).filter(
            Moment.user_id == user_id,
            Moment.created_at >= datetime.combine(diary_date, datetime.min.time()),
            Moment.created_at < datetime.combine(diary_date + timedelta(days=1), datetime.min.time())
        ).order_by(Moment.created_at.asc()).all()
        
        if not moments:
            return "今天没有记录任何瞬间。"
        
        # 构建瞬间数据
        moments_data = []
        for moment in moments:
            description = moment.ai_description_final or moment.ai_description_origin or moment.user_text
            if description:
                moments_data.append(description)
        
        # 使用AI生成日记
        diary_content = await self.ai_service.generate_daily_summary(moments_data)
        return diary_content
    
    def get_user_diaries(self, user_id: int, start_date: date = None, end_date: date = None, db: Session = None) -> List[DailyDiary]:
        """获取用户的日记列表"""
        query = db.query(DailyDiary).filter(DailyDiary.user_id == user_id)
        
        if start_date:
            query = query.filter(DailyDiary.diary_date >= start_date)
        if end_date:
            query = query.filter(DailyDiary.diary_date <= end_date)
        
        return query.order_by(DailyDiary.diary_date.desc()).all()
    
    def get_recent_diaries(self, user_id: int, days: int = 30, db: Session = None) -> List[DailyDiary]:
        """获取最近N天的日记"""
        start_date = datetime.now().date() - timedelta(days=days)
        
        return db.query(DailyDiary).filter(
            DailyDiary.user_id == user_id,
            DailyDiary.diary_date >= start_date
        ).order_by(DailyDiary.diary_date.desc()).all()
    
    def create_diary(self, user_id: int, diary_date: date, content: str, db: Session) -> DailyDiary:
        """创建日记记录"""
        # 检查是否已存在
        existing_diary = db.query(DailyDiary).filter(
            DailyDiary.user_id == user_id,
            DailyDiary.diary_date == diary_date
        ).first()
        
        if existing_diary:
            raise ValueError(f"Diary for {diary_date} already exists")
        
        diary = DailyDiary(
            user_id=user_id,
            diary_date=diary_date,
            content_origin=content,
            content_final=content
        )
        
        db.add(diary)
        db.commit()
        db.refresh(diary)
        
        return diary
    
    def update_diary_content(self, diary_id: int, content_final: str, db: Session) -> DailyDiary:
        """更新日记内容（人工修饰后）"""
        diary = db.query(DailyDiary).filter(DailyDiary.id == diary_id).first()
        if not diary:
            raise ValueError(f"Diary with id {diary_id} not found")
        
        diary.content_final = content_final
        diary.last_updated_at = datetime.now()
        
        db.commit()
        db.refresh(diary)
        
        return diary
    
    def mark_diary_pushed(self, diary_id: int, db: Session) -> DailyDiary:
        """标记日记已推送"""
        diary = db.query(DailyDiary).filter(DailyDiary.id == diary_id).first()
        if not diary:
            raise ValueError(f"Diary with id {diary_id} not found")
        
        diary.pushed_at = datetime.now()
        db.commit()
        db.refresh(diary)
        
        return diary 