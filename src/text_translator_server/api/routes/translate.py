from fastapi import APIRouter, Depends
from ollama import AsyncClient

from text_translator_server.api.deps import get_ollama_client
from text_translator_server.schemas.translate import TranslateRequestBody, TranslateResponseBody
from text_translator_server.services.translate import stop_model
from text_translator_server.services.translate import translate as translate_service


router = APIRouter(prefix="/translate", tags=["translate"])


@router.post(
    "",
    response_model=TranslateResponseBody,
    response_model_by_alias=True,
    summary="Translate Text",
    response_description="The translated text",
)
async def translate_endpoint(
    body: TranslateRequestBody,
    client: AsyncClient = Depends(get_ollama_client),
):
    """
    Translate text from a source language to a target language using the local Ollama model.

    - **sourceLang**: The language code of the input text (e.g., 'en')
    - **targetLang**: The language code you want to translate into (e.g., 'zh')
    - **sourceText**: The actual text content to translate
    """
    result_str = await translate_service(
        client, body.source_lang, body.target_lang, body.source_text
    )

    return TranslateResponseBody(translated_text=result_str)


@router.post(
    "/stop",
    summary="Stop Translation Model",
    response_description="Confirmation that the model has been unloaded",
)
async def stop_model_endpoint(
    client: AsyncClient = Depends(get_ollama_client),
):
    """
    Unload the translation model from memory (GPU/RAM).

    This is equivalent to running `ollama stop translategemma:latest` in the CLI.
    """
    await stop_model(client)

    return {"status": "stopped"}
