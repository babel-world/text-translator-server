"""Project path helpers."""

from __future__ import annotations

import os
from pathlib import Path


def get_repo_root() -> Path:
    """Return the project root (directory containing pyproject.toml)."""
    env_root = os.getenv("NLP_REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # src/nlp_server/utils/paths.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]
