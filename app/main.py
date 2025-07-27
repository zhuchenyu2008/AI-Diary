from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.endpoints import health, auth, moments, diaries

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="AI日记应用 - 智能记录生活瞬间，自动生成生动日记",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（用于本地存储的图片）
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 前端静态资源
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(moments.router, prefix="/api/v1", tags=["moments"])
app.include_router(diaries.router, prefix="/api/v1", tags=["diaries"])


@app.get("/", response_class=FileResponse)
async def root():
    """返回Web界面"""
    return FileResponse("web/index.html")


@app.get("/api/v1")
async def api_info():
    """API信息"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "AI日记应用API",
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "moments": "/api/v1/moments",
            "diaries": "/api/v1/diaries"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 