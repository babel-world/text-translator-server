from fastapi import APIRouter, HTTPException

from nlp_server.schemas.g2p import JaG2pRequestBody, JaG2pResponseBody
from nlp_server.services.g2p import g2p_ja


router = APIRouter(prefix="/g2p", tags=["g2p"])


@router.post(
    "/ja",
    response_model=JaG2pResponseBody,
    response_model_by_alias=True,
    summary="Japanese G2P",
    response_description="Phoneme token list",
)
def g2p_ja_endpoint(body: JaG2pRequestBody):
    """
    Convert Japanese text to phonemes.

    - **text**: Japanese input string
    - **mode**: `default` for basic pyopenjtalk.g2p, `prosody` for full-context prosody markers
    """
    try:
        phones = g2p_ja(body.text, body.mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"G2P failed: {exc}") from exc

    return JaG2pResponseBody(phones=phones)
