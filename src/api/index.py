from fastapi import APIRouter
from .routes.translate import router as translate_router

def create_api_router() -> APIRouter:
    api = APIRouter()
    api.include_router(translate_router, prefix="/api")
    return api