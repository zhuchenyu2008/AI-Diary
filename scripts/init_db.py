#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, Base
from app.core.config import settings


def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")

    try:
        # 导入所有模型，确保元数据已被填充
        from app.models import user, moment, diary  # noqa: F401

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功")
        
        # 测试数据库连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 数据库连接测试成功")
        
        print("数据库初始化完成！")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        print("请检查数据库配置和连接")
        sys.exit(1)


def create_sample_data():
    """创建示例数据（可选）"""
    print("正在创建示例数据...")
    
    try:
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        # 检查是否已有用户
        existing_user = db.query(User).filter(User.username == "demo").first()
        if existing_user:
            print("示例用户已存在，跳过创建")
            return
        
        # 创建示例用户
        demo_user = User(
            username="demo",
            email="demo@example.com",
            password_hash=get_password_hash("demo123")
        )
        
        db.add(demo_user)
        db.commit()
        print("✓ 示例用户创建成功 (用户名: demo, 密码: demo123)")
        
    except Exception as e:
        print(f"❌ 示例数据创建失败: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("AI日记应用 - 数据库初始化")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    
    # 询问是否创建示例数据
    try:
        create_sample = input("\n是否创建示例数据？(y/N): ").strip().lower()
        if create_sample in ['y', 'yes']:
            create_sample_data()
    except KeyboardInterrupt:
        print("\n操作已取消")
    
    print("\n初始化完成！")
    print("启动应用: uvicorn app.main:app --reload") 