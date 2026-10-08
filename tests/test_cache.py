from datetime import UTC, datetime, timedelta

import pytest

from app.cache import get_or_fetch

TTL = timedelta(hours=12)


class FakeColl:  # solo lo que usa get_or_fetch
    def __init__(self):
        self.docs = {}

    async def find_one(self, q):
        return self.docs.get(q["_id"])

    async def replace_one(self, q, doc, upsert=False):
        self.docs[q["_id"]] = doc


def fetcher(value=None, fail=False):
    calls = []

    async def fetch():
        calls.append(1)
        if fail:
            raise RuntimeError("api caída")
        return value

    fetch.calls = calls
    return fetch


@pytest.mark.asyncio
async def test_miss_fetches_and_stores():
    c, f = FakeColl(), fetcher({"a": 1})
    assert await get_or_fetch(c, "k", TTL, f) == {"a": 1}
    assert "k" in c.docs and len(f.calls) == 1


@pytest.mark.asyncio
async def test_fresh_does_not_fetch():
    c = FakeColl()
    c.docs["k"] = {"_id": "k", "data": "viejo", "fetched_at": datetime.now(UTC)}
    f = fetcher("nuevo")
    assert await get_or_fetch(c, "k", TTL, f) == "viejo" and not f.calls


@pytest.mark.asyncio
async def test_expired_refetches():
    c = FakeColl()
    c.docs["k"] = {"_id": "k", "data": "viejo", "fetched_at": datetime.now(UTC) - 2 * TTL}
    assert await get_or_fetch(c, "k", TTL, fetcher("nuevo")) == "nuevo"
    assert c.docs["k"]["data"] == "nuevo"


@pytest.mark.asyncio
async def test_expired_with_api_down_serves_stale():
    c = FakeColl()
    c.docs["k"] = {"_id": "k", "data": "viejo", "fetched_at": datetime.now(UTC) - 2 * TTL}
    assert await get_or_fetch(c, "k", TTL, fetcher(fail=True)) == "viejo"


@pytest.mark.asyncio
async def test_miss_with_api_down_raises():
    with pytest.raises(RuntimeError):
        await get_or_fetch(FakeColl(), "k", TTL, fetcher(fail=True))
