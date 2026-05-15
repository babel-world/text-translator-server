from fastapi import APIRouter
from src.schemas.translate import TranslateRequestBody, TranslateResponseBody
from src.services.translate import translate as translate_service


router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("", response_model=TranslateResponseBody)
async def translate_endpoint(body: TranslateRequestBody):
    result_str = translate_service(body.source_lang, body.target_lang, body.source_text)
    
    return TranslateResponseBody(translated_text=result_str)
