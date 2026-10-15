from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response

from app.deps import current_user, get_surveys
from app.repositories.surveys import SurveyRepository
from app.schemas import Rename, Survey

router = APIRouter(prefix="/surveys", tags=["surveys"])

Uid = Annotated[str, Depends(current_user)]
Repo = Annotated[SurveyRepository, Depends(get_surveys)]
SurveyId = Annotated[str, Path(min_length=1, max_length=64)]


@router.get("", response_model=list[Survey])
async def list_surveys(uid: Uid, repo: Repo):
    return await repo.list(uid)


@router.post("", response_model=Survey)
async def save_survey(survey: Survey, uid: Uid, repo: Repo):
    return await repo.upsert(uid, survey)


@router.patch("/{survey_id}", response_model=Survey)
async def rename_survey(survey_id: SurveyId, body: Rename, uid: Uid, repo: Repo):
    survey = await repo.rename(uid, survey_id, body.name)
    if survey is None:
        raise HTTPException(404, "Encuesta no encontrada")
    return survey


@router.delete("/{survey_id}", status_code=204)
async def delete_survey(survey_id: SurveyId, uid: Uid, repo: Repo):
    if not await repo.delete(uid, survey_id):
        raise HTTPException(404, "Encuesta no encontrada")
    return Response(status_code=204)
