from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.diary import DailyDiary
from app.services.diary_service import DiaryService

router = APIRouter()
security = HTTPBearer()


class DiaryResponse(BaseModel):
    id: int
    diary_date: date
    content_origin: str
    content_final: Optional[str]
    pushed_at: Optional[datetime]
    created_at: datetime


@router.get("/diaries", response_model=List[DiaryResponse])
async def get_diaries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    authorization: str = Depends(security),
    db: Session = Depends(get_db)
):
    """获取指定日期范围内的日记"""
    token = authorization.credentials
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    query = db.query(DailyDiary).filter(DailyDiary.user_id == user_id)
    
    if start_date:
        query = query.filter(DailyDiary.diary_date >= start_date)
    if end_date:
        query = query.filter(DailyDiary.diary_date <= end_date)
    
    diaries = query.order_by(DailyDiary.diary_date.desc()).offset(skip).limit(limit).all()
    
    return [
        DiaryResponse(
            id=diary.id,
            diary_date=diary.diary_date,
            content_origin=diary.content_origin,
            content_final=diary.content_final,
            pushed_at=diary.pushed_at,
            created_at=diary.created_at
        )
        for diary in diaries
    ]


@router.get("/diaries/recent", response_model=List[DiaryResponse])
async def get_recent_diaries(
    authorization: str = Depends(security),
    db: Session = Depends(get_db)
):
    """获取最近30天的日记"""
    token = authorization.credentials
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # 计算30天前的日期
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    diaries = db.query(DailyDiary).filter(
        DailyDiary.user_id == user_id,
        DailyDiary.diary_date >= thirty_days_ago
    ).order_by(DailyDiary.diary_date.desc()).all()
    
    return [
        DiaryResponse(
            id=diary.id,
            diary_date=diary.diary_date,
            content_origin=diary.content_origin,
            content_final=diary.content_final,
            pushed_at=diary.pushed_at,
            created_at=diary.created_at
        )
        for diary in diaries
    ]


@router.post("/diaries/summarize-today", response_model=DiaryResponse)
async def summarize_today(
    authorization: str = Depends(security),
    db: Session = Depends(get_db)
):
    """手动生成今天的日记"""
    token = authorization.credentials
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    today = datetime.now().date()
    
    # 检查今天是否已经有日记
    existing_diary = db.query(DailyDiary).filter(
        DailyDiary.user_id == user_id,
        DailyDiary.diary_date == today
    ).first()
    
    if existing_diary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Diary for today already exists"
        )
    
    # 生成日记
    diary_service = DiaryService()
    diary_content = await diary_service.generate_daily_diary(user_id, today, db)
    
    # 创建日记记录
    diary = DailyDiary(
        user_id=user_id,
        diary_date=today,
        content_origin=diary_content,
        content_final=diary_content
    )
    
    db.add(diary)
    db.commit()
    db.refresh(diary)
    
    return DiaryResponse(
        id=diary.id,
        diary_date=diary.diary_date,
        content_origin=diary.content_origin,
        content_final=diary.content_final,
        pushed_at=diary.pushed_at,
        created_at=diary.created_at
    ) 