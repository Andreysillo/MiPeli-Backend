from fastapi.testclient import TestClient

from app.deps import get_surveys, get_verifier
from app.main import app
from app.repositories.memory import MemorySurveyRepository


def verify(token: str) -> str:
    if token not in ("alice", "bob"):
        raise ValueError("bad token")
    return f"uid-{token}"


def client():
    repo = MemorySurveyRepository()
    app.dependency_overrides[get_verifier] = lambda: verify
    app.dependency_overrides[get_surveys] = lambda: repo
    return TestClient(app)


def auth(who: str) -> dict:
    return {"Authorization": f"Bearer {who}"}


def teardown_function():
    app.dependency_overrides.clear()


def test_without_token_is_401():
    assert client().get("/surveys").status_code == 401


def test_garbage_token_is_401():
    assert client().get("/surveys", headers=auth("nope")).status_code == 401


def test_valid_token_lists_empty():
    r = client().get("/surveys", headers=auth("alice"))
    assert r.status_code == 200 and r.json() == []
