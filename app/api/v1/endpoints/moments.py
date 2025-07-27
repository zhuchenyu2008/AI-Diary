from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id, get_token_from_header
from app.models.moment import Moment
from app.services.ai_service import AIService
from app.services.storage_service import StorageService

router = APIRouter()
security = HTTPBearer()


class MomentResponse(BaseModel):
    id: int
    ai_description_origin: Optional[str]
    ai_description_final: Optional[str]
    image_verified: bool
    created_at: datetime


@router.post("/moments", response_model=MomentResponse)
async def create_moment(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    authorization: str = Depends(security),
    db: Session = Depends(get_db)
):
    """创建瞬间，支持图片和文字，至少需要一项"""
    if not text and not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of text or image is required"
        )
    
    # 获取当前用户ID
    token = authorization.credentials
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # 处理图片上传
    image_url = None
    if image:
        storage_service = StorageService()
        image_url = await storage_service.upload_image(image)
    
    # 创建瞬间记录
    moment = Moment(
        user_id=user_id,
        user_text=text,
        image_url=image_url,
        image_verified=False
    )
    
    db.add(moment)
    db.commit()
    db.refresh(moment)
    
    # AI分析（异步处理）
    if text or image_url:
        ai_service = AIService()
        ai_description = await ai_service.analyze_moment(text, image_url)
        
        # 更新AI分析结果
        moment.ai_description_origin = ai_description
        moment.ai_description_final = ai_description  # 可以后续添加人工修饰逻辑
        db.commit()
    
    return MomentResponse(
        id=moment.id,
        ai_description_origin=moment.ai_description_origin,
        ai_description_final=moment.ai_description_final,
        image_verified=moment.image_verified,
        created_at=moment.created_at
    )


@router.get("/moments", response_model=List[MomentResponse])
async def get_moments(
    skip: int = 0,
    limit: int = 100,
    authorization: str = Depends(security),
    db: Session = Depends(get_db)
):
    """获取用户的瞬间列表"""
    token = authorization.credentials
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    moments = db.query(Moment).filter(
        Moment.user_id == user_id
    ).order_by(Moment.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        MomentResponse(
            id=moment.id,
            ai_description_origin=moment.ai_description_origin,
            ai_description_final=moment.ai_description_final,
            image_verified=moment.image_verified,
            created_at=moment.created_at
        )
        for moment in moments
    ] 