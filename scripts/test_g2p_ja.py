"""
Manual test script for POST /api/g2p/ja (Japanese G2P).

Usage:
  uv run python scripts/test_g2p_ja.py
  uv run python scripts/test_g2p_ja.py --mode prosody
  uv run python scripts/test_g2p_ja.py --run http --base-url http://127.0.0.1:19032
"""

import argparse
import sys

import httpx

from nlp_server.services.g2p import g2p_ja

SAMPLES = [
    "こんにちは。",
    "明日は晴れですか？",
    "学校へ行きます。",
]


def format_phones(phones: list[str]) -> str:
    return " ".join(phones)


def run_service(mode: str) -> None:
    print(f"=== Service: g2p_ja(mode={mode}) ===\n")
    for text in SAMPLES:
        phones = g2p_ja(text, mode=mode)  # type: ignore[arg-type]
        print(f"原文: {text}")
        print(f"  phones ({len(phones)}): {format_phones(phones)}")
        print()


def run_http(mode: str, base_url: str) -> None:
    print(f"=== HTTP: POST /api/g2p/ja mode={mode} ===\n")
    payload = {"text": SAMPLES[0], "mode": mode}
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        response = client.post("/api/g2p/ja", json=payload)
        response.raise_for_status()
        body = response.json()
        phones = body["phones"]
        print(f"原文: {SAMPLES[0]}")
        print(f"  phones ({len(phones)}): {format_phones(phones)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Japanese G2P")
    parser.add_argument(
        "--mode",
        choices=("default", "prosody", "all"),
        default="all",
        help="G2P mode (default: all — runs default and prosody)",
    )
    parser.add_argument(
        "--run",
        choices=("service", "http", "both"),
        default="service",
        help="service: direct call; http: API; both: run both",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:19032",
        help="Server base URL when --run http or both",
    )
    args = parser.parse_args()
    modes = ("default", "prosody") if args.mode == "all" else (args.mode,)

    if args.run in ("service", "both"):
        for i, mode in enumerate(modes):
            if i:
                print("-" * 60 + "\n")
            run_service(mode)
    if args.run in ("http", "both"):
        if args.run == "both" and modes:
            print("-" * 60 + "\n")
        for i, mode in enumerate(modes):
            if i:
                print("-" * 60 + "\n")
            run_http(mode, args.base_url)


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
