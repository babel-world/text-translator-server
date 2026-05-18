from fastapi import APIRouter, Depends
from ollama import AsyncClient

from text_translator_server.api.deps import get_ollama_client
from text_translator_server.schemas.translate import TranslateRequestBody, TranslateResponseBody
from text_translator_server.services.translate import translate as translate_service


router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("", response_model=TranslateResponseBody, response_model_by_alias=True)
async def translate_endpoint(
    body: TranslateRequestBody,
    client: AsyncClient = Depends(get_ollama_client),
):
    result_str = await translate_service(
        client, body.source_lang, body.target_lang, body.source_text
    )

    return TranslateResponseBody(translated_text=result_str)
