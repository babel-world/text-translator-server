"""Tests for worker timeout config, stderr tail, dispatch, and session."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from nlp_server.infra.worker.config import (
    clear_worker_config_cache,
    get_default_worker_timeout_sec,
    get_worker_timeout_sec,
    list_worker_aliases,
)
from nlp_server.infra.worker.dispatch import spawn_worker
from nlp_server.infra.worker.errors import (
    WorkerSpawnFailed,
    WorkerSpawnTimeout,
    tail_text,
)
from nlp_server.infra.worker.session import PersistentWorkerSession, get_worker_session

_FAKE_WORKER_SCRIPT = textwrap.dedent(
    """\
    import json
    import sys

    sys.stdout.write(json.dumps({"ok": True, "event": "ready"}) + "\\n")
    sys.stdout.flush()

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        cmd = payload.get("cmd")
        if cmd == "shutdown":
            sys.stdout.write(json.dumps({"ok": True, "event": "shutdown"}) + "\\n")
            sys.stdout.flush()
            break
        if cmd == "extract":
            sys.stderr.write("debug: " + ("x" * 200) + "\\n")
            sys.stderr.flush()
            sys.stdout.write(json.dumps({"ok": True, "result": "done"}) + "\\n")
            sys.stdout.flush()
        if cmd == "ping":
            sys.stdout.write(json.dumps({"ok": True, "loaded": True}) + "\\n")
            sys.stdout.flush()
    """
)


class WorkerConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_worker_config_cache()

    def tearDown(self) -> None:
        clear_worker_config_cache()

    def test_registry_starts_empty(self) -> None:
        self.assertEqual(list_worker_aliases(), [])

    def test_default_timeout_is_120(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_default_worker_timeout_sec(), 120.0)

    def test_env_alias_overrides_global(self) -> None:
        with patch.dict(
            os.environ,
            {
                "WORKER_SPAWN_TIMEOUT_SEC": "999",
                "WORKER_SPAWN_TIMEOUT_UNKNOWN_WORKER": "45",
            },
            clear=False,
        ):
            self.assertEqual(get_worker_timeout_sec("unknown-worker"), 45.0)


class WorkerErrorsTests(unittest.TestCase):
    def test_tail_text_keeps_suffix(self) -> None:
        long_text = "a" * 9000 + "TAIL"
        self.assertTrue(tail_text(long_text, max_bytes=100).endswith("TAIL"))


class WorkerDispatchTests(unittest.TestCase):
    def test_spawn_timeout_raises(self) -> None:
        with patch(
            "nlp_server.infra.worker.dispatch._load_run_worker_module"
        ) as load_mock:
            load_mock.return_value.spawn_worker.side_effect = subprocess.TimeoutExpired(
                cmd=["uv"],
                timeout=120,
            )
            with self.assertRaises(WorkerSpawnTimeout):
                spawn_worker("missing-worker", ["extract"])

    def test_spawn_failed_raises_with_tail(self) -> None:
        stderr = "x" * 9000 + "CUDA OOM"
        completed = subprocess.CompletedProcess(
            args=["uv"],
            returncode=1,
            stdout="",
            stderr=stderr,
        )
        with patch(
            "nlp_server.infra.worker.dispatch._load_run_worker_module"
        ) as load_mock:
            load_mock.return_value.spawn_worker.return_value = completed
            with self.assertRaises(WorkerSpawnFailed) as ctx:
                spawn_worker("missing-worker", ["extract"])
            self.assertIn("CUDA OOM", ctx.exception.stderr_tail)


class WorkerSessionTests(unittest.TestCase):
    ALIAS = "session-test"

    def tearDown(self) -> None:
        get_worker_session(self.ALIAS).stop()

    def test_request_ping_and_extract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            script_path = tmp_dir / "fake_worker.py"
            script_path.write_text(_FAKE_WORKER_SCRIPT, encoding="utf-8")
            input_path = tmp_dir / "input.txt"
            output_path = tmp_dir / "output.txt"
            input_path.write_text("hello", encoding="utf-8")

            def fake_build_worker_command(
                alias: str, worker_args: list[str]
            ) -> tuple[list[str], Path]:
                return [sys.executable, str(script_path), *worker_args], tmp_dir

            session = PersistentWorkerSession(self.ALIAS)
            with patch(
                "nlp_server.infra.worker.session._load_run_worker_module"
            ) as load_mock:
                load_mock.return_value.build_worker_command = fake_build_worker_command
                with patch(
                    "nlp_server.infra.worker.session.get_worker_timeout_sec",
                    return_value=5.0,
                ):
                    start = session.start()
                    self.assertTrue(start.newly_started)

                    ping = session.request({"cmd": "ping"})
                    self.assertTrue(ping.get("loaded"))

                    for i in range(10):
                        with self.subTest(iteration=i + 1):
                            response = session.request(
                                {
                                    "cmd": "extract",
                                    "input": str(input_path),
                                    "output": str(output_path),
                                }
                            )
                            self.assertEqual(response.get("result"), "done")

                    session.stop()


class RunWorkerRegistryTests(unittest.TestCase):
    def test_resolve_unknown_alias_fails(self) -> None:
        from workers.run_worker import resolve_worker

        with self.assertRaises(Exception) as ctx:
            resolve_worker("does-not-exist")
        self.assertIn("does-not-exist", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
