import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """设置测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user():
    """测试用户注册"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"


def test_register_user_without_email():
    """测试用户注册（无邮箱）"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"


def test_register_duplicate_username():
    """测试重复用户名注册"""
    # 先注册一个用户
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # 尝试注册相同用户名
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """测试登录成功"""
    # 先注册用户
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # 登录
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    """测试登录失败（错误密码）"""
    # 先注册用户
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # 使用错误密码登录
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user():
    """测试登录失败（用户不存在）"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "testpass123"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"] 