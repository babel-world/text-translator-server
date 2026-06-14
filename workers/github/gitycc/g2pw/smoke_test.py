"""Smoke test for g2pW worker (requires downloaded models)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import warnings
from pathlib import Path

from g2pw_worker.download import ensure_onnx_model_dir, is_onnx_model_complete, onnx_model_dir

WORKER_ROOT = Path(__file__).resolve().parent

# Polyphone-heavy simplified Chinese sentence (多音字：行/长/骑/步/考/觉/佩/道 等).
SAMPLE_TEXT = (
    "那位内行的银行行长，今天没有骑自行车，而是选择步行去考察各行各业的行情，"
    "大家都觉得他这行为真行，连老前辈都佩服他的道行。"
)

# Golden output for SAMPLE_TEXT (pinyin, simplified Chinese).
EXPECTED_PHONEMES = [
    [
        "na4",
        "wei4",
        "nei4",
        "hang2",
        "de5",
        "yin2",
        "hang2",
        "hang2",
        "zhang3",
        None,
        "jin1",
        "tian1",
        "mei2",
        "you3",
        "qi2",
        "zi4",
        "xing2",
        "che1",
        None,
        "er2",
        "shi4",
        "xuan3",
        "ze2",
        "bu4",
        "xing2",
        "qu4",
        "kao3",
        "cha2",
        "ge4",
        "hang2",
        "ge4",
        "ye4",
        "de5",
        "hang2",
        "qing2",
        None,
        "da4",
        "jia1",
        "dou1",
        "jue2",
        "de5",
        "ta1",
        "zhe4",
        "xing2",
        "wei2",
        "zhen1",
        "xing2",
        None,
        "lian2",
        "lao3",
        "qian2",
        "bei4",
        "dou1",
        "pei4",
        "fu2",
        "ta1",
        "de5",
        "dao4",
        "xing4",
        None,
    ]
]


def _model_ready() -> bool:
    return is_onnx_model_complete(onnx_model_dir())


def _serve_command() -> list[str]:
    """Match production: uv run g2pw serve (from worker project root)."""
    if shutil.which("uv") is None:
        raise unittest.SkipTest("'uv' not found in PATH")
    return ["uv", "run", "g2pw", "serve"]


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


class DownloadPathTests(unittest.TestCase):
    def test_onnx_model_dir_layout(self) -> None:
        path = onnx_model_dir()
        self.assertEqual(path.name, "G2PWModel")
        self.assertEqual(path.parent.name, "G2PWModel-v2-onnx")


class G2pSmokeTests(unittest.TestCase):
    @unittest.skipUnless(_model_ready(), "ONNX model not present under .models/")
    def test_example_sentence_one_shot(self) -> None:
        from g2pw_worker.infer import run_g2p

        text = SAMPLE_TEXT
        _log("g2p one-shot: loading model and running inference (may take ~30s)...")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", FutureWarning)
            result = json.loads(run_g2p(text))
        self.assertEqual(result, EXPECTED_PHONEMES)


class ServeProtocolTests(unittest.TestCase):
    @unittest.skipUnless(_model_ready(), "ONNX model not present under .models/")
    def test_stdio_serve_g2p_and_shutdown(self) -> None:
        cmd = _serve_command()
        _log(f"serve protocol: starting {' '.join(cmd)} (model load may take ~30s)...")
        proc = subprocess.Popen(
            cmd,
            cwd=str(WORKER_ROOT),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1,
        )
        assert proc.stdin is not None and proc.stdout is not None
        try:
            ready = json.loads(proc.stdout.readline())
            self.assertTrue(ready.get("ok"))
            self.assertEqual(ready.get("event"), "ready")
            _log("serve protocol: ready")

            proc.stdin.write(json.dumps({"cmd": "ping"}) + "\n")
            proc.stdin.flush()
            ping = json.loads(proc.stdout.readline())
            self.assertTrue(ping.get("loaded"))

            text = SAMPLE_TEXT
            _log("serve protocol: g2p request...")
            proc.stdin.write(json.dumps({"cmd": "g2p", "text": text}) + "\n")
            proc.stdin.flush()
            g2p = json.loads(proc.stdout.readline())
            self.assertTrue(g2p.get("ok"))
            self.assertEqual(json.loads(g2p["result"]), EXPECTED_PHONEMES)

            proc.stdin.write(json.dumps({"cmd": "shutdown"}) + "\n")
            proc.stdin.flush()
            shutdown = json.loads(proc.stdout.readline())
            self.assertEqual(shutdown.get("event"), "shutdown")
            _log("serve protocol: shutdown ok")
        finally:
            proc.wait(timeout=120)


if __name__ == "__main__":
    if not _model_ready():
        ensure_onnx_model_dir()
    unittest.main()
