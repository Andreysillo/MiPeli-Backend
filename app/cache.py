from datetime import UTC, datetime, timedelta

# Una sola colección "cache": la clave lleva el prefijo ("tmdb:movie:550") y cada llamada fija su vencimiento.
# El vencimiento es blando: si el dato está viejo se vuelve a pedir y, si la API falla, se sirve la copia vieja.
# El índice TTL (ensure_indexes) solo limpia lo abandonado.
CLEANUP = timedelta(days=90)


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=UTC)


async def get_or_fetch(coll, key: str, ttl: timedelta, fetch):
    doc = await coll.find_one({"_id": key})
    now = datetime.now(UTC)
    if doc and _aware(doc["fetched_at"]) + ttl > now:
        return doc["data"]
    try:
        data = await fetch()
    except Exception:
        if doc:
            return doc["data"]  # stale-if-error
        raise
    await coll.replace_one({"_id": key}, {"_id": key, "data": data, "fetched_at": now}, upsert=True)
    return data


async def ensure_indexes(coll) -> None:
    await coll.create_index("fetched_at", expireAfterSeconds=int(CLEANUP.total_seconds()))
