import os
from fastapi.testclient import TestClient

# Ensure minimal env vars for config
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.main import app

client = TestClient(app)


def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "AI Diary" in response.text
