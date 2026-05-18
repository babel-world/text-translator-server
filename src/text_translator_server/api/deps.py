from fastapi import Request
from ollama import AsyncClient


def get_ollama_client(request: Request) -> AsyncClient:
    return request.app.state.ollama_client
