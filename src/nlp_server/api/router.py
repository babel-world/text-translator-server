from fastapi import APIRouter
from nlp_server.api.routes.ollama import router as ollama_router


def create_api_router() -> APIRouter:
    api = APIRouter()
    api.include_router(ollama_router, prefix="/api")
    return api
