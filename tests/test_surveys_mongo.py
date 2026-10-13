import os
import uuid

import pytest
from pymongo import AsyncMongoClient

from app.repositories.mongo import MongoSurveyRepository
from app.repositories.surveys import MAX_SURVEYS
from app.schemas import Answers, Survey

# Necesita un Mongo real: en el CI corre contra un servicio; en local, con TEST_MONGODB_URI (ej. mongodb://localhost:27017)
URI = os.environ.get("TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="TEST_MONGODB_URI no está definida")


def make(id_: str, at: int, name: str | None = None) -> Survey:
    a = Answers(
        moods=["tension"], company="solo", avoid=[], duelPicks=[], liked=[], boosted=[], disliked=[], seen=[],
        numMovies=5,
    )
    return Survey(id=id_, at=at, name=name, titles=["Oldboy"], answers=a)


@pytest.fixture
async def repo():
    client = AsyncMongoClient(URI, tz_aware=True)
    db = client[f"mipeli_test_{uuid.uuid4().hex[:8]}"]  # base propia por prueba
    r = MongoSurveyRepository(db["surveys"])
    await r.ensure_indexes()
    yield r
    await client.drop_database(db.name)
    await client.close()


async def test_roundtrip_order_and_isolation(repo):
    await repo.upsert("u1", make("a", 1))
    await repo.upsert("u1", make("b", 2))
    await repo.upsert("u2", make("a", 3))  # mismo id en otra cuenta: no choca
    assert [s.id for s in await repo.list("u1")] == ["b", "a"]
    assert len(await repo.list("u2")) == 1
    assert await repo.rename("u2", "b", "x") is None
    assert await repo.delete("u2", "b") is False


async def test_update_keeps_name_and_rename_clears(repo):
    await repo.upsert("u", make("a", 1, name="Noche de terror"))
    assert (await repo.upsert("u", make("a", 2))).name == "Noche de terror"
    assert (await repo.rename("u", "a", "")).name is None
    assert await repo.delete("u", "a") is True


async def test_cap_drops_the_oldest(repo):
    for i in range(MAX_SURVEYS + 1):
        await repo.upsert("u", make(f"s{i}", i))
    ids = [s.id for s in await repo.list("u")]
    assert len(ids) == MAX_SURVEYS and "s0" not in ids and "s30" in ids
