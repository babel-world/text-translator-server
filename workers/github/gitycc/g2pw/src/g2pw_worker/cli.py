"""CLI entry for g2pW worker."""

from __future__ import annotations

import argparse
import os
import sys

from g2pw_worker import download, infer, serve


def _cmd_download(_args: argparse.Namespace) -> int:
    model_path = download.ensure_onnx_model_dir()
    model_source = download.ensure_bert_tokenizer_cache()
    print(f"model_path={model_path}")
    print(f"model_source={model_source}")
    return 0


def _cmd_g2p(args: argparse.Namespace) -> int:
    if args.cuda:
        os.environ["G2PW_USE_CUDA"] = "1"
    try:
        result = infer.run_g2p(args.text)
    except Exception as exc:
        print(f"❌ g2p failed: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


def _cmd_serve(_args: argparse.Namespace) -> int:
    return serve.run_serve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="g2pW ONNX inference worker")
    subparsers = parser.add_subparsers(dest="command")

    download_parser = subparsers.add_parser(
        "download",
        help="Download or resolve models into .models/",
    )
    download_parser.set_defaults(handler=_cmd_download)

    g2p_parser = subparsers.add_parser(
        "g2p",
        help="One-shot g2p in the current process (loads model each run)",
    )
    g2p_parser.add_argument(
        "--text",
        required=True,
        help="Input sentence (simplified or traditional Chinese)",
    )
    g2p_parser.add_argument(
        "--cuda",
        action="store_true",
        help="Use CUDAExecutionProvider for ONNX (sets G2PW_USE_CUDA=1)",
    )
    g2p_parser.set_defaults(handler=_cmd_g2p)

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run long-lived g2p server (JSON lines on stdin; for nlp-server session)",
    )
    serve_parser.set_defaults(handler=_cmd_serve)

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
