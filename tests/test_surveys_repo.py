import pytest

from app.repositories.memory import MemorySurveyRepository
from app.repositories.surveys import MAX_SURVEYS
from app.schemas import Answers, Survey


def make(id_: str, at: int, name: str | None = None) -> Survey:
    a = Answers(
        moods=["tension"], company="solo", avoid=[], duelPicks=[], liked=[], boosted=[], disliked=[], seen=[],
        numMovies=5,
    )
    return Survey(id=id_, at=at, name=name, titles=["Oldboy"], answers=a)


@pytest.fixture
def repo():
    return MemorySurveyRepository()


async def test_list_is_newest_first(repo):
    await repo.upsert("u", make("a", 1))
    await repo.upsert("u", make("b", 2))
    assert [s.id for s in await repo.list("u")] == ["b", "a"]


async def test_users_are_isolated(repo):
    await repo.upsert("u1", make("a", 1))
    assert await repo.list("u2") == []
    assert await repo.rename("u2", "a", "x") is None
    assert await repo.delete("u2", "a") is False
    assert len(await repo.list("u1")) == 1


async def test_update_without_name_keeps_the_name(repo):
    await repo.upsert("u", make("a", 1, name="Noche de terror"))
    await repo.upsert("u", make("a", 2))  # actualizar resultados no borra el nombre
    assert (await repo.list("u"))[0].name == "Noche de terror"


async def test_rename_and_clear(repo):
    await repo.upsert("u", make("a", 1))
    assert (await repo.rename("u", "a", "Mi noche")).name == "Mi noche"
    assert (await repo.rename("u", "a", "")).name is None


async def test_delete(repo):
    await repo.upsert("u", make("a", 1))
    assert await repo.delete("u", "a") is True
    assert await repo.delete("u", "a") is False


async def test_cap_drops_the_oldest(repo):
    for i in range(MAX_SURVEYS + 1):
        await repo.upsert("u", make(f"s{i}", i))
    ids = [s.id for s in await repo.list("u")]
    assert len(ids) == MAX_SURVEYS and "s0" not in ids and "s30" in ids


def test_schema_rejects_bad_input():
    with pytest.raises(ValueError):
        Answers(moods=["laugh", "tension", "feel"], company="solo", avoid=[], duelPicks=[], liked=[], boosted=[],
                disliked=[], seen=[], numMovies=5)
    with pytest.raises(ValueError):
        make("a", 1, name="x" * 51)
