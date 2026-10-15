import pytest
from fastapi.testclient import TestClient

from app.deps import get_surveys, get_verifier
from app.main import app
from app.repositories.memory import MemorySurveyRepository

ANSWERS = {
    "moods": ["tension"], "company": "solo", "avoid": [], "duelPicks": [], "liked": [],
    "boosted": [], "disliked": [], "seen": [], "numMovies": 5,
}


def body(id_="a", at=1, name=None):
    b = {"id": id_, "at": at, "titles": ["Oldboy"], "answers": ANSWERS}
    if name:
        b["name"] = name
    return b


def auth(who):
    return {"Authorization": f"Bearer {who}"}


@pytest.fixture
def c():
    repo = MemorySurveyRepository()
    app.dependency_overrides[get_verifier] = lambda: lambda t: f"uid-{t}"
    app.dependency_overrides[get_surveys] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_save_list_rename_delete(c):
    assert c.post("/surveys", json=body(), headers=auth("alice")).status_code == 200
    assert [s["id"] for s in c.get("/surveys", headers=auth("alice")).json()] == ["a"]
    r = c.patch("/surveys/a", json={"name": "Noche de terror"}, headers=auth("alice"))
    assert r.status_code == 200 and r.json()["name"] == "Noche de terror"
    # actualizar los resultados no borra el nombre
    assert c.post("/surveys", json=body(at=2), headers=auth("alice")).json()["name"] == "Noche de terror"
    assert c.delete("/surveys/a", headers=auth("alice")).status_code == 204
    assert c.get("/surveys", headers=auth("alice")).json() == []


def test_users_cannot_touch_each_others_surveys(c):
    c.post("/surveys", json=body(), headers=auth("alice"))
    assert c.get("/surveys", headers=auth("bob")).json() == []
    assert c.patch("/surveys/a", json={"name": "x"}, headers=auth("bob")).status_code == 404
    assert c.delete("/surveys/a", headers=auth("bob")).status_code == 404
    assert len(c.get("/surveys", headers=auth("alice")).json()) == 1


def test_missing_survey_is_404(c):
    assert c.patch("/surveys/zzz", json={"name": "x"}, headers=auth("alice")).status_code == 404
    assert c.delete("/surveys/zzz", headers=auth("alice")).status_code == 404


def test_invalid_body_is_422(c):
    bad = body()
    bad["answers"] = {**ANSWERS, "moods": ["laugh", "tension", "feel"]}
    assert c.post("/surveys", json=bad, headers=auth("alice")).status_code == 422
    assert c.post("/surveys", json=body(name="x" * 51), headers=auth("alice")).status_code == 422
    assert c.patch("/surveys/a", json={"name": "x" * 51}, headers=auth("alice")).status_code == 422


def test_all_routes_require_a_token(c):
    assert c.post("/surveys", json=body()).status_code == 401
    assert c.patch("/surveys/a", json={"name": "x"}).status_code == 401
    assert c.delete("/surveys/a").status_code == 401
