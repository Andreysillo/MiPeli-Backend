from typing import Protocol

from app.schemas import Survey

MAX_SURVEYS = 30  # por usuario; al pasar, se borra la más antigua


class SurveyRepository(Protocol):
    """Encuestas guardadas. Cada operación se limita al `uid` dado: nadie toca datos de otro usuario."""

    async def list(self, uid: str) -> list[Survey]:
        """Las más recientes primero."""

    async def upsert(self, uid: str, survey: Survey) -> Survey:
        """Crea o actualiza por id. Actualizar sin `name` conserva el que ya tenía."""

    async def rename(self, uid: str, survey_id: str, name: str) -> Survey | None:
        """Cambia solo el nombre ("" lo quita). None si no existe."""

    async def delete(self, uid: str, survey_id: str) -> bool:
        """False si no existía."""
