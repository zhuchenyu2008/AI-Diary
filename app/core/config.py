from typing import Optional, List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # 应用配置
    app_name: str = Field(default="AI日记应用", env="APP_NAME")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    api_v1_str: str = Field(default="/api/v1", env="API_V1_STR")
    
    # 数据库配置
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AI服务配置
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # 对象存储配置
    storage_type: str = Field(default="s3", env="STORAGE_TYPE")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # 阿里云OSS配置
    oss_access_key_id: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_ID")
    oss_access_key_secret: Optional[str] = Field(default=None, env="OSS_ACCESS_KEY_SECRET")
    oss_endpoint: Optional[str] = Field(default=None, env="OSS_ENDPOINT")
    oss_bucket_name: Optional[str] = Field(default=None, env="OSS_BUCKET_NAME")
    
    # Telegram配置
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # 安全配置
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 文件上传配置
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        env="ALLOWED_IMAGE_TYPES"
    )
    
    # 任务调度配置
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")
    
    # 监控配置
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings() 