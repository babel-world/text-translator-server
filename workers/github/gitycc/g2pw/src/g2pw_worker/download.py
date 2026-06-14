"""Resolve and download g2pW ONNX model assets."""

from __future__ import annotations

import io
import os
import threading
import zipfile
from pathlib import Path

import requests

MODEL_URL = "https://storage.googleapis.com/esun-ai/g2pW/G2PWModel-v2-onnx.zip"
MODELS_WRAPPER = "G2PWModel-v2-onnx"
MODEL_DIR_NAME = "G2PWModel"
BERT_MODEL_ID = "bert-base-chinese"
BERT_CACHE_DIR_NAME = "bert-base-chinese"

_ONNX_FILE = "g2pw.onnx"
_VERSION_FILE = "version"
_MIN_ONNX_BYTES = 1_000_000

_MODEL_RESOLUTION_LOCK = threading.Lock()


def worker_root() -> Path:
    """Worker project root (directory containing pyproject.toml)."""
    return Path(__file__).resolve().parent.parent.parent


def models_dir() -> Path:
    return worker_root() / ".models"


def onnx_wrapper_dir() -> Path:
    return models_dir() / MODELS_WRAPPER


def onnx_model_dir() -> Path:
    return onnx_wrapper_dir() / MODEL_DIR_NAME


def bert_cache_dir() -> Path:
    return models_dir() / BERT_CACHE_DIR_NAME


def is_onnx_model_complete(path: Path) -> bool:
    version = path / _VERSION_FILE
    onnx = path / _ONNX_FILE
    if not version.is_file() or not onnx.is_file():
        return False
    return onnx.stat().st_size >= _MIN_ONNX_BYTES


def _download_and_extract_onnx(wrapper_dir: Path) -> None:
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(MODEL_URL, allow_redirects=True, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(wrapper_dir)

    inner = onnx_model_dir()
    if not is_onnx_model_complete(inner):
        raise RuntimeError(
            f"Downloaded archive did not produce a valid model at {inner}"
        )


def ensure_onnx_model_dir() -> Path:
    """Return inner G2PWModel/ path, downloading the ONNX zip if needed."""
    target = onnx_model_dir()
    with _MODEL_RESOLUTION_LOCK:
        if is_onnx_model_complete(target):
            return target.resolve()
        _download_and_extract_onnx(onnx_wrapper_dir())
        if not is_onnx_model_complete(target):
            raise RuntimeError(f"ONNX model incomplete after download: {target}")
        return target.resolve()


def run_download() -> tuple[Path, str]:
    """Resolve or download all model assets; return (onnx_dir, bert_model_id)."""
    return ensure_onnx_model_dir(), ensure_bert_tokenizer_cache()


def ensure_bert_tokenizer_cache() -> str:
    """Download/cache bert-base-chinese tokenizer under .models/; return hub id."""
    cache_root = models_dir()
    cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_root))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(cache_root))

    from transformers import BertTokenizer

    BertTokenizer.from_pretrained(BERT_MODEL_ID)
    return BERT_MODEL_ID
