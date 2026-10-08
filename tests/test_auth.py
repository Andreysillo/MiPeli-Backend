from fastapi.testclient import TestClient

from app.deps import get_verifier
from app.main import app


def fake_verify(token: str) -> str:
    if token != "good":
        raise ValueError("bad token")
    return "uid-123"


def client():
    app.dependency_overrides[get_verifier] = lambda: fake_verify
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_me_without_token_is_401():
    assert client().get("/me").status_code == 401


def test_me_with_garbage_token_is_401():
    assert client().get("/me", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_me_with_valid_token_returns_uid():
    r = client().get("/me", headers={"Authorization": "Bearer good"})
    assert r.status_code == 200 and r.json() == {"uid": "uid-123"}
