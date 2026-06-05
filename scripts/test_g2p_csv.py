"""
Manual test script for G2P manifest CSV processing.

Usage:
  uv run python scripts/test_g2p_csv.py
  uv run python scripts/test_g2p_csv.py --input .local/manbo_manifest.csv
  uv run python scripts/test_g2p_csv.py --mode http --base-url http://127.0.0.1:19032
"""

import argparse
import csv
import io
import sys
from pathlib import Path

import httpx

from nlp_server.schemas.g2p import OUTPUT_COLUMNS
from nlp_server.services.g2p.csv_batch import process_manifest_csv, summarize_manifest_csv

DEFAULT_INPUT = Path(".local/manbo_manifest.csv")
PREVIEW_ROWS = 3


def read_csv_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def print_header_check(csv_text: str) -> None:
    reader = csv.DictReader(io.StringIO(csv_text))
    fieldnames = reader.fieldnames or []
    print(f"列数: {len(fieldnames)}")
    print(f"列名: {','.join(fieldnames)}")
    print(f"期望列: {','.join(OUTPUT_COLUMNS)}")
    print(f"列顺序匹配: {fieldnames == list(OUTPUT_COLUMNS)}")


def print_preview(csv_text: str, limit: int = PREVIEW_ROWS) -> None:
    reader = csv.DictReader(io.StringIO(csv_text))
    print(f"\n前 {limit} 行预览:")
    for index, row in enumerate(reader):
        if index >= limit:
            break
        print(
            f"  [{index}] status={row.get('status')} "
            f"phones_count={row.get('phone_count')} "
            f"error={row.get('error') or '-'}"
        )
        print(f"       text={row.get('text', '')[:60]}")
        phones = row.get("phones") or ""
        if phones:
            print(f"       phones={phones[:80]}{'...' if len(phones) > 80 else ''}")


def run_service(input_path: Path) -> str:
    csv_text = read_csv_text(input_path)
    return process_manifest_csv(csv_text)


def run_http(input_path: Path, base_url: str) -> str:
    csv_bytes = input_path.read_bytes()
    with httpx.Client(base_url=base_url, timeout=600.0) as client:
        response = client.post(
            "/api/g2p/csv",
            files={"file": (input_path.name, csv_bytes, "text/csv")},
        )
        response.raise_for_status()
        return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="Test G2P manifest CSV processing")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input manifest CSV path (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--mode",
        choices=("service", "http"),
        default="service",
        help="service: call csv_batch directly; http: call FastAPI endpoint",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:19032",
        help="Server base URL when --mode http",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write output CSV",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Input: {args.input}")
    print(f"Mode : {args.mode}")

    if args.mode == "service":
        result_csv = run_service(args.input)
    else:
        result_csv = run_http(args.input, args.base_url)

    summary = summarize_manifest_csv(result_csv)
    print("\n=== Summary ===")
    print(f"total : {summary['total']}")
    print(f"ok    : {summary['ok']}")
    print(f"skip  : {summary['skip']}")
    print(f"error : {summary['error']}")

    print("\n=== Output Header ===")
    print_header_check(result_csv)
    print_preview(result_csv)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result_csv, encoding="utf-8")
        print(f"\nOutput written to: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
