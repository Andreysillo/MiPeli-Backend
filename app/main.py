from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient

from app.cache import ensure_indexes
from app.config import settings
from app.deps import current_user
from app.schemas import Me


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = None
    if settings.mongodb_uri:
        client = AsyncMongoClient(settings.mongodb_uri, tz_aware=True)
        app.state.db = client[settings.mongodb_db]
        await ensure_indexes(app.state.db["cache"])
    yield
    if client:
        await client.close()


app = FastAPI(title="MiPeli API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# No toca la base: Render lo llama seguido
@app.get("/health")
async def health():
    return {"status": "ok"}


# Provisional: prueba la autenticación de punta a punta; /surveys la reemplaza
@app.get("/me", response_model=Me)
async def me(uid: Annotated[str, Depends(current_user)]):
    return Me(uid=uid)
