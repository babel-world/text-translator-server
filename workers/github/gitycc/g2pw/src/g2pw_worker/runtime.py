"""Thread-safe G2PWConverter runtime."""

from __future__ import annotations

import gc
import os
import sys
import threading
from typing import TYPE_CHECKING

from g2pw_worker import download

if TYPE_CHECKING:
    from g2pw.api import G2PWConverter

_runtime_lock = threading.Lock()
_converter: G2PWConverter | None = None
_vendor_ready = False


def _ensure_vendor_path() -> None:
    global _vendor_ready
    if _vendor_ready:
        return
    vendor_root = download.worker_root() / "vendor"
    vendor_str = str(vendor_root)
    if vendor_str not in sys.path:
        sys.path.insert(0, vendor_str)
    _vendor_ready = True


def _use_cuda() -> bool:
    return os.getenv("G2PW_USE_CUDA", "").strip().lower() in {"1", "true", "yes"}


def is_loaded() -> bool:
    with _runtime_lock:
        return _converter is not None


def warm_up() -> None:
    """Load model into memory if not already loaded."""
    get_converter()


def get_converter() -> G2PWConverter:
    """Return a cached G2PWConverter configured for simplified Chinese pinyin."""
    global _converter
    _ensure_vendor_path()
    from g2pw.api import G2PWConverter

    model_dir = download.ensure_onnx_model_dir()
    model_source = download.ensure_bert_tokenizer_cache()

    with _runtime_lock:
        if _converter is not None:
            return _converter

        _converter = G2PWConverter(
            model_dir=str(model_dir),
            style="pinyin",
            model_source=model_source,
            num_workers=0,
            turnoff_tqdm=True,
            enable_non_tradional_chinese=True,
            use_cuda=_use_cuda(),
        )
        return _converter


def release_runtime() -> None:
    """Drop cached converter so memory can be reclaimed."""
    global _converter
    with _runtime_lock:
        _converter = None
    gc.collect()
