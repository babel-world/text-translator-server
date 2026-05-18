from fastapi import APIRouter
from text_translator_server.schemas.translate import TranslateRequestBody, TranslateResponseBody
from text_translator_server.services.translate import translate as translate_service


router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("", response_model=TranslateResponseBody)
async def translate_endpoint(body: TranslateRequestBody):
    result_str = await translate_service(
        body.source_lang, body.target_lang, body.source_text
    )

    return TranslateResponseBody(translated_text=result_str)
