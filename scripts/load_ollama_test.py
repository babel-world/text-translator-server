"""
Simple load test for the Ollama translation API.

Prerequisites:
  1. Ollama is running with translategemma pulled
  2. Server is running: uv run nlp-server

Usage:
  uv run python scripts/load_ollama_test.py
  uv run python scripts/load_ollama_test.py --base-url http://127.0.0.1:19032

Sample results (2026-05-25, local Ollama + translategemma, after /start warmup):
  min/avg/max are per-request round-trip times, not total batch duration.
  Total run (188 requests): ~2 min 4 sec.

    # | success |       min |       avg |       max
  --- |---------|-----------|-----------|-----------
    1 |   1/1   |     1.34s |     1.34s |     1.34s
    2 |   2/2   |     1.03s |     1.29s |     1.54s
    5 |   5/5   |     1.12s |     2.13s |     3.15s
   10 |  10/10  |     1.26s |     3.62s |     6.00s
   20 |  20/20  |     1.36s |     6.24s |    11.13s
   50 |  50/50  |     2.19s |    14.97s |    27.69s
  100 | 100/100 |     3.76s |    29.43s |    54.68s
"""

import argparse
import asyncio
import statistics
import sys
import time

import httpx

BASE_URL = "http://127.0.0.1:19032"
CONCURRENCY_LEVELS = [1, 2, 5, 10, 20, 50, 100]
REQUEST_TIMEOUT = 600.0

TRANSLATE_PAYLOAD = {
    "sourceLang": "zh",
    "targetLang": "en",
    "sourceText": (
        "全民制作人们，大家好，我是练习时长两年半的，个人练习生蔡徐坤，"
        "喜欢唱、跳、rap、篮球。"
    ),
}


async def warmup(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/ollama/start")
    if response.status_code != 200:
        raise RuntimeError(
            f"start failed: HTTP {response.status_code}, body={response.text}"
        )

    body = response.json()
    if body.get("status") != "started":
        raise RuntimeError(f"start failed: unexpected body={body}")


async def translate_once(client: httpx.AsyncClient, index: int) -> float:
    start = time.perf_counter()
    response = await client.post("/api/ollama/translate", json=TRANSLATE_PAYLOAD)
    elapsed = time.perf_counter() - start

    if response.status_code != 200:
        raise RuntimeError(
            f"request #{index} failed: HTTP {response.status_code}, body={response.text}"
        )

    return elapsed


async def run_level(client: httpx.AsyncClient, concurrency: int) -> list[float]:
    tasks = [translate_once(client, i) for i in range(concurrency)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed_times: list[float] = []
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            raise RuntimeError(f"request #{index} failed: {result}") from result
        elapsed_times.append(result)

    return elapsed_times


def print_summary(concurrency: int, elapsed_times: list[float]) -> None:
    print(
        f"{concurrency:>3} | "
        f"{len(elapsed_times):>3}/{concurrency:<3} | "
        f"{min(elapsed_times):>8.2f}s | "
        f"{statistics.mean(elapsed_times):>8.2f}s | "
        f"{max(elapsed_times):>8.2f}s"
    )


async def main(base_url: str) -> None:
    async with httpx.AsyncClient(base_url=base_url, timeout=REQUEST_TIMEOUT) as client:
        print(f"Base URL: {base_url}")
        print("Warming up model via POST /api/ollama/start ...")
        await warmup(client)
        print("Warmup OK.\n")

        print(" concurrency | success |      min |      avg |      max")
        print("-------------|---------|----------|----------|----------")

        for concurrency in CONCURRENCY_LEVELS:
            elapsed_times = await run_level(client, concurrency)
            print_summary(concurrency, elapsed_times)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test for Ollama translation API")
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help=f"Server base URL (default: {BASE_URL})",
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(args.base_url))
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
