import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from dependencies import get_db
from main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def get_token(username: str = "tester") -> str:
    response = client.post(f"/auth/token?username={username}")
    return response.json()["access_token"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_post():
    token = get_token()
    payload = {
        "title": "My first post",
        "content": "Post content",
        "tags": ["fastapi", "postgres"],
        "author_id": 1,
    }
    created = client.post(
        "/posts", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert created.status_code == 201
    post_id = created.json()["id"]

    fetched = client.get(f"/posts/{post_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == payload["title"]


def test_post_requires_auth():
    payload = {"title": "No auth", "content": "x", "tags": [], "author_id": 1}
    response = client.post("/posts", json=payload)
    assert response.status_code == 401


def test_update_and_delete_post():
    token = get_token("editor")
    payload = {"title": "Initial", "content": "Body", "tags": [], "author_id": 2}
    created = client.post(
        "/posts", json=payload, headers={"Authorization": f"Bearer {token}"}
    )
    post_id = created.json()["id"]

    updated = client.put(
        f"/posts/{post_id}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    deleted = client.delete(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert deleted.status_code == 204

