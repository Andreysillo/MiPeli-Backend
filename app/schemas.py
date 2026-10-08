from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

Mood = Literal["laugh", "tension", "feel", "mind", "epic", "scare", "cozy", "real"]
Company = Literal["solo", "couple", "friends", "family"]
Short = Annotated[str, StringConstraints(max_length=120)]  # un título (hoy) o un id de TMDB (después)
TitleList = Annotated[list[Short], Field(max_length=100)]

MAX_NAME = 50


class Me(BaseModel):
    uid: str


class Answers(BaseModel):
    """Las respuestas con que se hizo una encuesta (las plataformas son preferencia de hoy y no se guardan)."""

    moods: Annotated[list[Mood], Field(max_length=2)]
    maxRuntime: Annotated[int, Field(ge=1, le=600)] | None = None
    company: Company
    avoid: Annotated[list[Annotated[str, StringConstraints(max_length=40)]], Field(max_length=30)]
    duelPicks: TitleList
    liked: TitleList
    boosted: TitleList
    disliked: TitleList
    seen: TitleList
    numMovies: Annotated[int, Field(ge=1, le=10)]


class Survey(BaseModel):
    id: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    at: int  # ms desde epoch, como Date.now() del frontend
    name: Annotated[str, StringConstraints(max_length=MAX_NAME)] | None = None
    titles: TitleList  # foto de lo recomendado (títulos hoy; ids de TMDB después)
    answers: Answers


class Rename(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_NAME)]  # vacío = quitar el nombre
