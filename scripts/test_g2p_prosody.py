"""
Manual test script for Japanese prosody G2P.

Usage:
  uv run python scripts/test_g2p_prosody.py
  uv run python scripts/test_g2p_prosody.py --mode prosody
  uv run python scripts/test_g2p_prosody.py --mode aligned
  uv run python scripts/test_g2p_prosody.py --mode pipeline
"""

import argparse
import sys

from nlp_server.services.g2p.constants.symbols2 import symbols
from nlp_server.services.g2p.japanese import get_japanese_text_input
from nlp_server.services.g2p.utils.prosody_g2p import extract_prosody
from nlp_server.services.g2p.utils.symbol_alignment import align_to_vits_symbols

SAMPLES = [
    "こんにちは。",
    "明日は晴れですか？",
    "学校へ行きます。",
]

PUNCTUATION_SAMPLES = [
    "こんにちは。ありがとう！",
]

SYMBOL_SET = set(symbols)


def format_phones(phones: list[str]) -> str:
    return " ".join(phones)


def print_vocab_check(aligned: list[str]) -> None:
    invalid = [phone for phone in aligned if phone not in SYMBOL_SET]
    if invalid:
        print(f"  词表外符号: {invalid}")
    else:
        print("  词表校验: OK")


def run_prosody() -> None:
    print("=== Mode: prosody (extract_prosody only) ===\n")

    for text in SAMPLES + PUNCTUATION_SAMPLES:
        phones = extract_prosody(text)
        print(f"原文: {text}")
        print(f"  韵律序列: {format_phones(phones)}")
        print(f"  token 数: {len(phones)}")
        print("  说明: OpenJTalk 会把标点转为 _ / $ / ?，不会保留 。！ 等显式标点")
        print()


def run_aligned() -> None:
    print("=== Mode: aligned (extract_prosody + align_to_vits_symbols) ===\n")

    for text in SAMPLES + PUNCTUATION_SAMPLES:
        raw = extract_prosody(text)
        aligned = align_to_vits_symbols(raw)

        print(f"原文: {text}")
        print(f"  原始韵律: {format_phones(raw)}")
        print(f"  对齐结果: {format_phones(aligned)}")
        print(f"  token 数: {len(raw)} -> {len(aligned)}")
        print_vocab_check(aligned)
        print("  说明: 未做标点缝合，rep_map 基本不会生效")
        print()


def run_pipeline() -> None:
    print("=== Mode: pipeline (get_japanese_text_input) ===\n")

    for text in SAMPLES + PUNCTUATION_SAMPLES:
        result = get_japanese_text_input(text)
        aligned = result["phones"]
        punct_tokens = [phone for phone in aligned if phone in {".", "!", "?", ",", "…"}]

        print(f"原文: {result['text']}")
        print(f"  对齐结果: {format_phones(aligned)}")
        print(f"  显式标点: {format_phones(punct_tokens) if punct_tokens else '(无)'}")
        print(f"  phone_ids: {result['phone_ids']}")
        print(f"  token 数: {len(aligned)}")
        print_vocab_check(aligned)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual test for Japanese prosody G2P")
    parser.add_argument(
        "--mode",
        choices=("prosody", "aligned", "pipeline", "all"),
        default="all",
        help=(
            "prosody: extract only; aligned: direct align; "
            "pipeline: split-stitch pipeline; all: all modes (default)"
        ),
    )
    args = parser.parse_args()

    modes = ("prosody", "aligned", "pipeline") if args.mode == "all" else (args.mode,)
    for index, mode in enumerate(modes):
        if index > 0:
            print("-" * 60 + "\n")
        if mode == "prosody":
            run_prosody()
        elif mode == "aligned":
            run_aligned()
        elif mode == "pipeline":
            run_pipeline()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
