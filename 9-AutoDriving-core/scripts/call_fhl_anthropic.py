#!/usr/bin/env python3
"""CLI utility to test and call FHL Anthropic Claude models directly.

Usage:
  python3 scripts/call_fhl_anthropic.py "Hello, Claude!"
  python3 scripts/call_fhl_anthropic.py --model claude-opus-5 "Explain DARC route gating"
  python3 scripts/call_fhl_anthropic.py --model claude-haiku-4-5-20251001 --json "Extract POI from: visit library"
  python3 scripts/call_fhl_anthropic.py --interactive
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://www.fhl.mom")
DEFAULT_API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

SUPPORTED_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-sonnet-5",
    "claude-opus-4-6",
    "claude-opus-4-7",
    "claude-opus-4-8",
    "claude-opus-5",
    "claude-fable-5",
]


def call_fhl_anthropic(
    user_prompt: str,
    system_prompt: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1000,
    temperature: float = 0.0,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str = DEFAULT_API_KEY,
) -> dict:
    if not api_key:
        raise RuntimeError("ANTHROPIC_AUTH_TOKEN is missing; load your private environment file first")
    url = f"{base_url.rstrip('/')}/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            elapsed = time.perf_counter() - t0
            res = json.loads(resp.read().decode("utf-8"))
            content_list = res.get("content", [])
            text = "".join(part.get("text", "") for part in content_list if isinstance(part, dict))
            usage = res.get("usage", {})
            return {
                "success": True,
                "model": model,
                "text": text,
                "elapsed_seconds": round(elapsed, 2),
                "usage": usage,
                "raw": res,
            }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - t0
        err_msg = exc.read().decode("utf-8", errors="replace")
        return {
            "success": False,
            "model": model,
            "error": f"HTTP {exc.code}: {err_msg}",
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return {
            "success": False,
            "model": model,
            "error": str(exc),
            "elapsed_seconds": round(elapsed, 2),
        }


def main():
    parser = argparse.ArgumentParser(description="Call FHL Anthropic Claude models directly via CLI")
    parser.add_argument("prompt", nargs="?", default="", help="Prompt to send to Claude")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, choices=SUPPORTED_MODELS, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--system", "-s", default="", help="System prompt")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens (default: 1000)")
    parser.add_argument("--temperature", "-t", type=float, default=0.0, help="Temperature (default: 0.0)")
    parser.add_argument("--json", action="store_true", help="Request JSON-only format in prompt")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive terminal chat session")
    parser.add_argument("--raw", action="store_true", help="Print raw response JSON")
    args = parser.parse_args()

    if args.interactive:
        print(f"=== FHL Claude Interactive Session ({args.model}) ===")
        print("Type 'exit' or 'quit' to end.\n")
        while True:
            try:
                user_in = input("You: ").strip()
                if not user_in:
                    continue
                if user_in.lower() in ["exit", "quit"]:
                    print("Bye!")
                    break
                print(f"Claude ({args.model}) thinking...", end="", flush=True)
                res = call_fhl_anthropic(
                    user_prompt=user_in,
                    system_prompt=args.system,
                    model=args.model,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                )
                print(f"\rClaude ({args.model}, {res['elapsed_seconds']}s):")
                if res["success"]:
                    print(res["text"])
                    if "usage" in res:
                        u = res["usage"]
                        print(f"  [Tokens: in={u.get('input_tokens')}, out={u.get('output_tokens')}]")
                else:
                    print(f"[ERROR] {res['error']}")
                print("-" * 50)
            except (KeyboardInterrupt, EOFError):
                print("\nBye!")
                break
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    user_text = args.prompt
    if args.json and "JSON" not in user_text:
        user_text += "\nReturn valid JSON only."

    print(f"Calling FHL Anthropic ({args.model})...", file=sys.stderr)
    res = call_fhl_anthropic(
        user_prompt=user_text,
        system_prompt=args.system,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    if args.raw:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if res["success"]:
        print(res["text"])
        u = res.get("usage", {})
        print(f"\n[✓ Done in {res['elapsed_seconds']}s | Model: {res['model']} | In: {u.get('input_tokens')}, Out: {u.get('output_tokens')} tokens]", file=sys.stderr)
    else:
        print(f"[✕ FAILED in {res['elapsed_seconds']}s] {res['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
