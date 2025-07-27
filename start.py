#!/usr/bin/env python3
"""
AI日记应用启动脚本
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def main():
    """主函数"""
    print("=" * 50)
    print("AI日记应用")
    print("=" * 50)
    print(f"应用名称: {settings.app_name}")
    print(f"调试模式: {settings.debug}")
    print(f"API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    # 检查必要的环境变量
    required_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请检查 .env 文件配置")
        sys.exit(1)
    
    # 创建必要的目录
    os.makedirs("uploads/images", exist_ok=True)
    
    # 启动应用
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main() 