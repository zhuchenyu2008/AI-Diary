#!/usr/bin/env python3
"""
创建管理员用户脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin_user():
    """创建管理员用户"""
    print("=" * 50)
    print("创建管理员用户")
    print("=" * 50)
    
    try:
        # 获取用户输入
        username = input("请输入用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return
        
        password = input("请输入密码: ").strip()
        if not password:
            print("❌ 密码不能为空")
            return
        
        email = input("请输入邮箱 (可选): ").strip()
        if not email:
            email = None
        
        # 连接数据库
        db = SessionLocal()
        
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ 用户 '{username}' 已存在")
            return
        
        # 创建新用户
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✓ 管理员用户创建成功!")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email or '未设置'}")
        print(f"   用户ID: {new_user.id}")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user() 