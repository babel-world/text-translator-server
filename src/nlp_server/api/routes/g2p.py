from fastapi import APIRouter, HTTPException, UploadFile
from starlette.responses import Response

from nlp_server.services.g2p.csv_batch import process_manifest_csv


router = APIRouter(prefix="/g2p", tags=["g2p"])


@router.post(
    "/csv",
    summary="Convert manifest CSV to G2P CSV",
    response_description="CSV with original columns plus G2P result columns",
)
def g2p_csv_endpoint(file: UploadFile):
    """
    Upload a manifest CSV and receive a new CSV with G2P results appended.

    Input columns:
    `filename,speaker,language,text,probability`

    Output columns:
    `filename,speaker,language,text,probability,norm_text,phones,phone_count,word2ph,status,error`

    Privacy preprocessing (hard-coded):
    - only `language == ja`
    - only `probability > 0.95`
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .csv file")

    try:
        raw_bytes = file.file.read()
        csv_text = raw_bytes.decode("utf-8-sig")
        result_csv = process_manifest_csv(csv_text)
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"G2P CSV processing failed: {exc}") from exc

    return Response(content=result_csv, media_type="text/csv; charset=utf-8")
