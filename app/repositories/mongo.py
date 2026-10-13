from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.repositories.surveys import MAX_SURVEYS
from app.schemas import Survey


class MongoSurveyRepository:
    """Encuestas en Mongo. `_id` = "uid:id": un mismo id de encuesta en dos cuentas nunca choca."""

    def __init__(self, coll):
        self.coll = coll

    async def ensure_indexes(self) -> None:
        await self.coll.create_index([("uid", ASCENDING), ("at", DESCENDING)])

    @staticmethod
    def _key(uid: str, survey_id: str) -> str:
        return f"{uid}:{survey_id}"

    async def list(self, uid: str) -> list[Survey]:
        docs = await self.coll.find({"uid": uid}).sort("at", DESCENDING).to_list(MAX_SURVEYS)
        return [Survey.model_validate(d) for d in docs]

    async def upsert(self, uid: str, survey: Survey) -> Survey:
        fields = survey.model_dump(exclude_none=True)  # sin `name` no se toca el que ya tenía
        doc = await self.coll.find_one_and_update(
            {"_id": self._key(uid, survey.id)},
            {"$set": {**fields, "uid": uid}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        # Pasado el tope, se borran las más antiguas
        extra = await self.coll.find({"uid": uid}, {"_id": 1}).sort("at", DESCENDING).skip(MAX_SURVEYS).to_list(None)
        if extra:
            await self.coll.delete_many({"_id": {"$in": [d["_id"] for d in extra]}})
        return Survey.model_validate(doc)

    async def rename(self, uid: str, survey_id: str, name: str) -> Survey | None:
        doc = await self.coll.find_one_and_update(
            {"_id": self._key(uid, survey_id)},
            {"$set": {"name": name or None}},
            return_document=ReturnDocument.AFTER,
        )
        return Survey.model_validate(doc) if doc else None

    async def delete(self, uid: str, survey_id: str) -> bool:
        return (await self.coll.delete_one({"_id": self._key(uid, survey_id)})).deleted_count == 1
