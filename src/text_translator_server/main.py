from contextlib import asynccontextmanager

from fastapi import FastAPI
from ollama import AsyncClient

from text_translator_server.api.router import create_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncClient(host="http://127.0.0.1:11434")
    app.state.ollama_client = client
    try:
        yield
    finally:
        await client._client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(create_api_router())
