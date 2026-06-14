"""g2pW inference helpers (one-shot CLI and serve handlers)."""

from __future__ import annotations

import json

from g2pw_worker.runtime import get_converter


def g2p_to_json_string(text: str) -> str:
    """Convert one sentence to a JSON string of per-character pinyin."""
    converter = get_converter()
    return json.dumps(converter(text), ensure_ascii=False)


def run_g2p(text: str) -> str:
    """One-shot g2p in the current process (CLI debugging)."""
    return g2p_to_json_string(text)
