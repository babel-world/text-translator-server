from fastapi import FastAPI
from text_translator_server.api.router import create_api_router

app = FastAPI()
app.include_router(create_api_router())
