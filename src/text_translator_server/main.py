from fastapi import FastAPI
from .api.index import create_api_router

app = FastAPI()
app.include_router(create_api_router())
