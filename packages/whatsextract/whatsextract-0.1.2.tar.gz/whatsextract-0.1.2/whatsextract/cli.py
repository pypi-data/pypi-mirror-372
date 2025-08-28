# sdk-py/whatsextract/cli.py
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import List, Optional

import requests


def _request(
    method: str,
    url: str,
    *,
    api_key: str,
    json_body: Optional[dict] = None,
    timeout: int = 30,
) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        resp = requests.request(method, url, headers=headers, json=json_body, timeout=timeout)
    except Exception as e:
        raise SystemExit(f"Network error: {e}")

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail")
        except Exception:
            detail = resp.text.strip()
        raise SystemExit(f"HTTP {resp.status_code}: {detail or 'request failed'}")

    try:
        return resp.json()
    except Exception:
        raise SystemExit("Invalid JSON response")


def _do_extract(base_url: str, api_key: str, message: str, mode: str, timeout: int):
    t0 = time.perf_counter()
    data = _request(
        "POST",
        f"{base_url.rstrip('/')}/v2/extract",
        api_key=api_key,
        json_body={"message": message, "mode": mode},
        timeout=timeout,
    )
    dt_ms = int((time.perf_counter() - t0) * 1000)
    data_out = {**data, "_cli_processing_time_ms": dt_ms}
    print(json.dumps(data_out, indent=2, ensure_ascii=False))


def _do_batch(
    base_url: str,
    api_key: str,
    messages: List[str],
    mode: str,
    timeout: int,
    webhook_url: Optional[str],
):
    payload = {
        "messages": messages,
        "mode": mode,
        "skip_errors": True,
    }
    if webhook_url:
        payload["webhook_url"] = webhook_url

    data = _request(
        "POST",
        f"{base_url.rstrip('/')}/v2/batch",
        api_key=api_key,
        json_body=payload,
        timeout=timeout,
    )
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _do_usage(base_url: str, api_key: str, timeout: int):
    data = _request(
        "GET",
        f"{base_url.rstrip('/')}/v2/usage",
        api_key=api_key,
        timeout=timeout,
    )
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _do_validate(base_url: str, message: str, timeout: int):
    # /v2/validate is public (no auth)
    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/v2/validate",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json={"message": message},
            timeout=timeout,
        )
        if resp.status_code >= 400:
            raise SystemExit(f"HTTP {resp.status_code}: {resp.text.strip()}")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        raise SystemExit(f"Network error: {e}")


def _read_messages_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="whatsextract",
        description="WhatsExtract CLI — extract contacts from text via the WhatsExtract API",
    )
    p.add_argument("--api-key", help="API key (Bearer)", required=False)
    p.add_argument("--base-url", default="http://localhost:8080", help="API base URL")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout (seconds)")
    p.add_argument("--max-retries", type=int, default=3, help="(reserved, not used by CLI)")

    sub = p.add_subparsers(dest="cmd", required=True)

    # extract
    sp = sub.add_parser("extract", help="Extract a single message")
    sp.add_argument("message", help="Message text to extract from")
    sp.add_argument("--mode", choices=["lite", "full"], default="lite")

    # batch
    sp = sub.add_parser("batch", help="Batch extract from multiple messages")
    src = sp.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="Path to file with one message per line")
    src.add_argument("--messages", nargs="+", help="Messages provided inline")
    sp.add_argument("--mode", choices=["lite", "full"], default="lite")
    sp.add_argument("--webhook-url", help="Optional webhook callback URL")

    # usage
    sub.add_parser("usage", help="Show account usage")

    # validate
    sp = sub.add_parser("validate", help="Check if a message likely contains extractable content")
    sp.add_argument("message", help="Message text to validate")

    return p


def main(argv: Optional[List[str]] = None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Commands that require an API key:
    needs_key = args.cmd in {"extract", "batch", "usage"}
    if needs_key and not args.api_key:
        parser.error("--api-key is required for this command")

    if args.cmd == "extract":
        _do_extract(args.base_url, args.api_key, args.message, args.mode, args.timeout)
    elif args.cmd == "batch":
        if args.file:
            messages = _read_messages_from_file(args.file)
        else:
            messages = args.messages or []
        if not messages:
            parser.error("No messages provided")
        _do_batch(args.base_url, args.api_key, messages, args.mode, args.timeout, args.webhook_url)
    elif args.cmd == "usage":
        _do_usage(args.base_url, args.api_key, args.timeout)
    elif args.cmd == "validate":
        _do_validate(args.base_url, args.message, args.timeout)
    else:
        parser.print_help()


# Backwards compat if something imports cli:cli
def cli():  # pragma: no cover
    main()


if __name__ == "__main__":  # pragma: no cover
    main()
