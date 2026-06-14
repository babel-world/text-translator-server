"""Long-running serve loop: load model once, handle JSON-line requests on stdin."""

from __future__ import annotations

import json
import sys
from typing import Any

from g2pw_worker import infer, runtime


def _write_response(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    cmd = payload.get("cmd")
    if cmd == "ping":
        runtime.warm_up()
        return {"ok": True, "loaded": runtime.is_loaded()}
    if cmd == "g2p":
        text = payload.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("missing or empty 'text'")
        result = infer.g2p_to_json_string(text)
        return {"ok": True, "result": result}
    if cmd == "shutdown":
        runtime.release_runtime()
        return {"ok": True, "event": "shutdown"}
    return {"ok": False, "error": f"unknown cmd: {cmd!r}"}


def run_serve() -> int:
    """Load g2pW once, then process one JSON object per stdin line."""
    try:
        runtime.warm_up()
    except Exception as exc:
        _write_response({"ok": False, "error": str(exc), "event": "ready"})
        return 1

    _write_response({"ok": True, "event": "ready"})

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_response({"ok": False, "error": f"invalid json: {exc}"})
            continue

        if payload.get("cmd") == "shutdown":
            _write_response({"ok": True, "event": "shutdown"})
            return 0

        try:
            response = _handle_request(payload)
        except Exception as exc:
            response = {"ok": False, "error": str(exc)}
        _write_response(response)

    runtime.release_runtime()
    return 0
