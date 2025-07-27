from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    # 检查AI服务（这里可以添加实际的AI服务检查）
    ai_service_status = "ok"
    
    return {
        "status": "ok",
        "db": db_status,
        "ai_service": ai_service_status,
        "app_name": settings.app_name
    } 