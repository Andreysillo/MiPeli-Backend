from app.repositories.surveys import MAX_SURVEYS
from app.schemas import Survey


class MemorySurveyRepository:
    """Para pruebas y desarrollo sin base: mismas reglas que la de Mongo."""

    def __init__(self):
        self._by_user: dict[str, dict[str, Survey]] = {}

    async def list(self, uid: str) -> list[Survey]:
        return sorted(self._by_user.get(uid, {}).values(), key=lambda s: s.at, reverse=True)

    async def upsert(self, uid: str, survey: Survey) -> Survey:
        mine = self._by_user.setdefault(uid, {})
        old = mine.get(survey.id)
        if old and survey.name is None:
            survey = survey.model_copy(update={"name": old.name})
        mine[survey.id] = survey
        for s in sorted(mine.values(), key=lambda s: s.at)[: max(0, len(mine) - MAX_SURVEYS)]:
            del mine[s.id]
        return survey

    async def rename(self, uid: str, survey_id: str, name: str) -> Survey | None:
        mine = self._by_user.get(uid, {})
        if survey_id not in mine:
            return None
        mine[survey_id] = mine[survey_id].model_copy(update={"name": name or None})
        return mine[survey_id]

    async def delete(self, uid: str, survey_id: str) -> bool:
        return self._by_user.get(uid, {}).pop(survey_id, None) is not None
