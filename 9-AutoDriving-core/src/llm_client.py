#!/usr/bin/env python3
"""Shared dependency-free LLM client for research projects.

This module standardizes the provider transport that first lived inside
`3-smga/benchmarks/diagnostic_v0/model_calling_runner.py` and was then reused by
`5-Telephone/sim/llm.py`.

Design goals:
- keep API keys in environment variables only;
- support mock, OpenAI-compatible chat completions, and Responses-style APIs;
- make model/version/temperature/base_url explicit and reproducible;
- expose a tiny `LLM.complete()` / `LLM.complete_json()` wrapper for project code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Iterator


DEFAULT_PROVIDER = "mock"
DEFAULT_MODEL = "mock-baseline"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_WIRE_API = "chat_completions"
DEFAULT_BASE_URL = "https://api.openai.com"


class ModelClient(Protocol):
    def complete(self, prompt: dict[str, Any]) -> str:
        """Return raw text for one prompt."""


@dataclass(frozen=True)
class LLMConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    wire_api: str = DEFAULT_WIRE_API
    base_url: str = DEFAULT_BASE_URL
    temperature: float = DEFAULT_TEMPERATURE
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    json_mode: bool = True
    retries: int = 0
    retry_sleep: float = 1.0
    sleep: float = 0.0
    max_concurrency: int = 1
    omit_temperature: bool = False
    reasoning_effort: str | None = None
    max_output_tokens: int | None = None
    stream: bool = False
    service_tier: str | None = None
    store: bool | None = None
    responses_input_mode: str = "messages"
    input_char_limit: int | None = None
    transport: str = "urllib"
    api_key_env: str | None = None


@dataclass(frozen=True)
class MockClient:
    model: str

    def complete(self, prompt: dict[str, Any]) -> str:
        object.__setattr__(self, "last_usage", None)
        return json.dumps(
            {
                "model": self.model,
                "response_text": "Mock response. Configure a real provider before reporting model results.",
            },
            ensure_ascii=False,
        )


@dataclass(frozen=True)
class OpenAICompatibleChatClient:
    config: LLMConfig
    api_key: str

    def complete(self, prompt: dict[str, Any]) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": str(prompt.get("system_prompt", ""))},
                {"role": "user", "content": str(prompt.get("user_prompt", ""))},
            ],
        }
        if not self.config.omit_temperature:
            payload["temperature"] = self.config.temperature
        if self.config.json_mode:
            payload["response_format"] = {"type": "json_object"}
        if self.config.max_output_tokens is not None:
            payload["max_completion_tokens"] = self.config.max_output_tokens
        url = normalize_endpoint(self.config.base_url, "chat_completions")
        if self.config.transport == "curl":
            data = post_json_with_curl(
                url,
                payload,
                self.api_key,
                self.config.timeout,
            )
        elif self.config.transport == "urllib":
            data = post_json(
                url,
                payload,
                self.api_key,
                self.config.timeout,
            )
        else:
            raise ValueError(f"unsupported transport: {self.config.transport}")
        object.__setattr__(self, "last_usage", data.get("usage"))
        choices = data.get("choices")
        if not choices:
            raise RuntimeError(f"chat completions response has no choices: {data}")
        message = choices[0].get("message", {})

        # Try standard content field first
        content = message.get("content")
        if isinstance(content, str):
            return content

        # DeepSeek V4 reasoning mode: extract from reasoning_content
        reasoning_content = message.get("reasoning_content")
        if isinstance(reasoning_content, str):
            # Try to extract JSON from reasoning content
            # The reasoning content may be truncated, but often contains valid JSON
            extracted = parse_embedded_json_object(reasoning_content)
            if extracted is not None:
                return json.dumps(extracted, ensure_ascii=False)
            # If no valid JSON found but we have reasoning content, return it as-is
            # (the caller's JSON parser will handle it)
            return reasoning_content

        raise RuntimeError(f"chat completions response has no text content: {data}")


@dataclass(frozen=True)
class AnthropicMessagesClient:
    config: LLMConfig
    api_key: str

    def _post_with_curl(self, url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
        cmd = [
            "curl", "-sS", url,
            "-H", f"x-api-key: {self.api_key}",
            "-H", "anthropic-version: 2023-06-01",
            "-H", "Content-Type: application/json",
            "--data-binary", json.dumps(payload),
        ]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"curl request failed: {completed.stderr.strip()}")
        try:
            return json.loads(completed.stdout)
        except Exception as e:
            raise RuntimeError(f"failed to parse json from curl output: {completed.stdout[:200]}") from e

    def complete(self, prompt: dict[str, Any]) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        system_prompt = str(prompt.get("system_prompt", "")).strip()
        user_prompt = str(prompt.get("user_prompt", "")).strip()
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": self.config.max_output_tokens or 1600,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if not self.config.omit_temperature:
            payload["temperature"] = self.config.temperature

        if self.config.transport == "curl":
            data = self._post_with_curl(url, payload, self.config.timeout)
        else:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                try:
                    data = self._post_with_curl(url, payload, self.config.timeout)
                except Exception as curl_exc:
                    if isinstance(exc, urllib.error.HTTPError):
                        detail = exc.read().decode("utf-8", errors="replace")
                        raise RuntimeError(f"provider HTTP {exc.code}: {detail}") from exc
                    raise RuntimeError(f"provider request failed: {exc} | curl fallback failed: {curl_exc}") from exc

        usage = data.get("usage")
        object.__setattr__(self, "last_response", data)
        object.__setattr__(self, "last_usage", usage)
        content = data.get("content", [])
        text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if not text:
            raise RuntimeError(f"anthropic response has no text content: {data}")
        return text


def stream_sse_events(
    url: str, payload: dict[str, Any], api_key: str, timeout: int
) -> "Iterator[dict[str, Any]]":
    """Yield parsed SSE `data:` events from a streaming Responses call."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        for raw in response:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if not chunk or chunk == "[DONE]":
                continue
            try:
                yield json.loads(chunk)
            except json.JSONDecodeError:
                continue


@dataclass(frozen=True)
class OpenAICompatibleResponsesClient:
    config: LLMConfig
    api_key: str

    def complete(self, prompt: dict[str, Any]) -> str:
        payload = build_responses_payload(prompt, self.config)
        if self.config.stream:
            return self._complete_streaming(payload)
        if self.config.transport == "curl":
            data = post_json_with_curl(
                normalize_endpoint(self.config.base_url, "responses"),
                payload,
                self.api_key,
                self.config.timeout,
            )
        elif self.config.transport == "urllib":
            data = post_json(
                normalize_endpoint(self.config.base_url, "responses"),
                payload,
                self.api_key,
                self.config.timeout,
            )
        else:
            raise ValueError(f"unsupported transport: {self.config.transport}")
        object.__setattr__(self, "last_usage", data.get("usage"))
        content = extract_responses_text(data)
        if not isinstance(content, str):
            raise RuntimeError(f"responses response has no text content: {data}")
        return content

    def _complete_streaming(self, payload: dict[str, Any]) -> str:
        """Read the answer from the SSE delta stream.

        Some reasoning-model deployments (e.g. the Codex-relay gpt-5.6-*
        variants) emit their text ONLY as `response.output_text.delta` events:
        the terminal `response.completed` object still contains just a bare
        `reasoning` item with encrypted content and no `message`, while
        reporting status "completed". A non-streaming client therefore loses the
        answer entirely with no error, so those models require streaming.
        """
        request = dict(payload)
        request["stream"] = True
        url = normalize_endpoint(self.config.base_url, "responses")
        text_parts: list[str] = []
        usage: dict[str, Any] | None = None
        for event in stream_sse_events(url, request, self.api_key, self.config.timeout):
            kind = event.get("type", "")
            if kind == "response.output_text.delta":
                text_parts.append(str(event.get("delta", "")))
            elif kind in {"response.completed", "response.incomplete"}:
                usage = (event.get("response") or {}).get("usage")
            elif kind == "error" or kind.endswith(".error"):
                raise RuntimeError(f"streaming responses error: {event}")
        object.__setattr__(self, "last_usage", usage)
        content = "".join(text_parts)
        if not content.strip():
            raise RuntimeError("streaming responses produced no output_text deltas")
        return content


class LLM:
    """Tiny project-facing wrapper around the standard transport."""

    def __init__(
        self,
        config: Path | str | LLMConfig | None = None,
        *,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        json_mode: bool | None = None,
    ) -> None:
        self.config = resolve_config(
            config,
            provider=provider,
            model=model,
            temperature=temperature,
            json_mode=json_mode,
        )
        self.client = build_client(self.config)
        self.telemetry: list[dict[str, Any]] = []

    def complete(self, system: str, user: str) -> str:
        prompt = {"system_prompt": system, "user_prompt": user}
        attempts = 0
        started = time.perf_counter()
        while True:
            attempts += 1
            try:
                response = self.client.complete(prompt)
                latency = time.perf_counter() - started
                usage = normalize_usage(getattr(self.client, "last_usage", None))
                self.telemetry.append(
                    build_telemetry_record(
                        call_index=len(self.telemetry) + 1,
                        system=system,
                        user=user,
                        response=response,
                        attempts=attempts,
                        latency=latency,
                        usage=usage,
                        success=True,
                    )
                )
                return response
            except Exception as exc:
                if attempts > self.config.retries:
                    latency = time.perf_counter() - started
                    self.telemetry.append(
                        build_telemetry_record(
                            call_index=len(self.telemetry) + 1,
                            system=system,
                            user=user,
                            response="",
                            attempts=attempts,
                            latency=latency,
                            usage=None,
                            success=False,
                            error=type(exc).__name__,
                        )
                    )
                    raise
                time.sleep(self.config.retry_sleep)

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        parsed = parse_response_json(self.complete(system, user))
        return parsed if isinstance(parsed, dict) else {}

    def telemetry_summary(self) -> dict[str, Any]:
        successful = [record for record in self.telemetry if record["success"]]
        exact_usage = [record for record in successful if record["usage_source"] == "provider"]
        return {
            "calls": len(self.telemetry),
            "successful_calls": len(successful),
            "failed_calls": len(self.telemetry) - len(successful),
            "latency_seconds": round(
                sum(float(record["latency_seconds"]) for record in self.telemetry), 3
            ),
            "provider_usage_calls": len(exact_usage),
            "input_tokens": sum(int(record["input_tokens"]) for record in successful),
            "output_tokens": sum(int(record["output_tokens"]) for record in successful),
            "total_tokens": sum(int(record["total_tokens"]) for record in successful),
            "usage_complete": bool(successful) and len(exact_usage) == len(successful),
        }


def normalize_usage(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    input_tokens = value.get("input_tokens", value.get("prompt_tokens"))
    output_tokens = value.get("output_tokens", value.get("completion_tokens"))
    total_tokens = value.get("total_tokens")
    if not isinstance(input_tokens, (int, float)) or not isinstance(
        output_tokens, (int, float)
    ):
        return None
    if not isinstance(total_tokens, (int, float)):
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "total_tokens": int(total_tokens),
    }


def build_telemetry_record(
    *,
    call_index: int,
    system: str,
    user: str,
    response: str,
    attempts: int,
    latency: float,
    usage: dict[str, int] | None,
    success: bool,
    error: str | None = None,
) -> dict[str, Any]:
    input_chars = len(system) + len(user)
    output_chars = len(response)
    if usage is None:
        input_tokens = (input_chars + 3) // 4
        output_tokens = (output_chars + 3) // 4
        usage_source = "character_estimate"
    else:
        input_tokens = usage["input_tokens"]
        output_tokens = usage["output_tokens"]
        total_tokens = usage["total_tokens"]
        usage_source = "provider"
    if usage is None:
        total_tokens = input_tokens + output_tokens
    record: dict[str, Any] = {
        "call_index": call_index,
        "prompt_sha256": hashlib.sha256(
            (system + "\0" + user).encode("utf-8")
        ).hexdigest(),
        "attempts": attempts,
        "latency_seconds": round(latency, 3),
        "input_chars": input_chars,
        "output_chars": output_chars,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "usage_source": usage_source,
        "success": success,
    }
    if error:
        record["error"] = error
    return record


def load_config(path: Path | str) -> LLMConfig:
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return config_from_dict(data)


def config_from_dict(data: dict[str, Any]) -> LLMConfig:
    store = data.get("store")
    if "disable_response_storage" in data:
        store = not bool(data["disable_response_storage"])
    return LLMConfig(
        provider=str(data.get("provider", DEFAULT_PROVIDER)),
        model=str(data.get("model", DEFAULT_MODEL)),
        wire_api=str(data.get("wire_api", DEFAULT_WIRE_API)),
        base_url=str(data.get("base_url", DEFAULT_BASE_URL)),
        temperature=float(data.get("temperature", DEFAULT_TEMPERATURE)),
        timeout=int(data.get("timeout", DEFAULT_TIMEOUT_SECONDS)),
        json_mode=bool(data.get("json_mode", True)),
        retries=int(data.get("retries", 0)),
        retry_sleep=float(data.get("retry_sleep", 1.0)),
        sleep=float(data.get("sleep", 0.0)),
        max_concurrency=max(1, int(data.get("max_concurrency", 1))),
        omit_temperature=bool(data.get("omit_temperature", False)),
        reasoning_effort=optional_str(data.get("reasoning_effort", data.get("model_reasoning_effort"))),
        max_output_tokens=(
            int(data["max_output_tokens"]) if data.get("max_output_tokens") else None
        ),
        stream=bool(data.get("stream", False)),
        service_tier=optional_str(data.get("service_tier")),
        store=None if store is None else bool(store),
        responses_input_mode=str(data.get("responses_input_mode", "messages")),
        input_char_limit=None if data.get("input_char_limit") is None else int(data["input_char_limit"]),
        transport=str(data.get("transport", "urllib")),
        api_key_env=optional_str(data.get("api_key_env")),
    )


def resolve_config(
    config: Path | str | LLMConfig | None,
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    json_mode: bool | None = None,
) -> LLMConfig:
    if isinstance(config, LLMConfig) or type(config).__name__ == "LLMConfig":
        base = config
    elif config is None:
        base = LLMConfig()
    else:
        base = load_config(config)
    return LLMConfig(
        **{
            **base.__dict__,
            "provider": provider or base.provider,
            "model": model or base.model,
            "temperature": base.temperature if temperature is None else float(temperature),
            "json_mode": base.json_mode if json_mode is None else bool(json_mode),
        }
    )


def build_client(config: LLMConfig) -> ModelClient:
    if config.provider == "mock":
        return MockClient(model=config.model)
    api_key = get_api_key(config.provider, config.api_key_env)
    if config.wire_api == "chat_completions":
        return OpenAICompatibleChatClient(config=config, api_key=api_key)
    if config.wire_api == "responses":
        return OpenAICompatibleResponsesClient(config=config, api_key=api_key)
    if config.wire_api in {"anthropic_messages", "messages"}:
        return AnthropicMessagesClient(config=config, api_key=api_key)
    raise ValueError(f"unsupported wire_api: {config.wire_api}")


def get_api_key(provider: str, api_key_env: str | None = None) -> str:
    env_names = []
    if api_key_env:
        env_names.append(api_key_env)
    if provider == "anthropic":
        env_names.extend(["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"])
        claude_env = Path.home() / ".config/fhl/claude.env"
        if claude_env.exists():
            for line in claude_env.read_text(encoding="utf-8").splitlines():
                if "ANTHROPIC_AUTH_TOKEN=" in line:
                    token = line.split("ANTHROPIC_AUTH_TOKEN=", 1)[1].strip().strip('"').strip("'")
                    if token:
                        os.environ["ANTHROPIC_AUTH_TOKEN"] = token
    env_names.append(f"{provider.upper()}_API_KEY")
    env_names.append("OPENAI_API_KEY")
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            return value
    raise RuntimeError(f"missing API key; set one of: {', '.join(dict.fromkeys(env_names))}")


def normalize_endpoint(base_url: str, wire_api: str) -> str:
    if base_url.endswith("/chat/completions") or base_url.endswith("/responses"):
        return base_url
    if wire_api == "responses":
        return f"{base_url.rstrip('/')}/v1/responses"
    return f"{base_url.rstrip('/')}/v1/chat/completions"


def build_responses_payload(prompt: dict[str, Any], config: LLMConfig) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": config.model}
    if config.responses_input_mode == "string":
        text = format_prompt_as_string(prompt)
        payload["input"] = truncate(text, config.input_char_limit)
    elif config.responses_input_mode == "user":
        payload["input"] = truncate(str(prompt.get("user_prompt", "")).strip(), config.input_char_limit)
    elif config.responses_input_mode == "messages":
        payload["input"] = [
            {"role": "system", "content": str(prompt.get("system_prompt", ""))},
            {"role": "user", "content": str(prompt.get("user_prompt", ""))},
        ]
    else:
        raise ValueError(f"unsupported responses_input_mode: {config.responses_input_mode}")
    if not config.omit_temperature:
        payload["temperature"] = config.temperature
    if config.json_mode:
        payload["text"] = {"format": {"type": "json_object"}}
    if config.reasoning_effort:
        payload["reasoning"] = {"effort": config.reasoning_effort}
    if config.max_output_tokens:
        # Reasoning variants (e.g. gpt-5.6-luna / -terra) silently return a bare
        # `reasoning` item with no `message` when the output budget is too small
        # to finish — and still report status "completed" with no
        # incomplete_details, so the truncation is invisible. An explicit budget
        # is required for those models to emit an answer at all.
        payload["max_output_tokens"] = config.max_output_tokens
    if config.service_tier:
        payload["service_tier"] = config.service_tier
    if config.store is not None:
        payload["store"] = config.store
    return payload


def post_json(url: str, payload: dict[str, Any], api_key: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"provider HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"provider request failed: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"provider returned non-object JSON: {data}")
    return data


def post_json_with_curl(url: str, payload: dict[str, Any], api_key: str, timeout: int) -> dict[str, Any]:
    config_path: str | None = None
    try:
        escaped_key = api_key.replace("\\", "\\\\").replace('"', '\\"')
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="llm-curl-",
            suffix=".conf",
            delete=False,
        ) as config_file:
            config_path = config_file.name
            os.chmod(config_path, 0o600)
            config_file.write(
                f'header = "Authorization: Bearer {escaped_key}"\n'
                'header = "Content-Type: application/json"\n'
            )
        cmd = [
            "curl",
            "-sS",
            "--http1.1",
            url,
            "--config",
            config_path,
        ]
        if "fhl.mom" in url:
            cmd.extend([
                "--resolve", "www.fhl.mom:443:104.21.224.5",
                "--resolve", "fhl.mom:443:104.21.224.5",
            ])
        cmd.extend([
            "--data-binary",
            "@-",
            "--write-out",
            "\n%{http_code}",
        ])
        completed = subprocess.run(
            cmd,
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"provider curl request timed out after {timeout} seconds"
        ) from None
    finally:
        if config_path is not None:
            Path(config_path).unlink(missing_ok=True)
    if completed.returncode != 0:
        raise RuntimeError(f"curl request failed: {completed.stderr.strip()}")
    body, separator, status_text = (completed.stdout or "").rpartition("\n")
    if not separator or not status_text.isdigit():
        raise RuntimeError(f"curl response missing HTTP status: {completed.stdout}")
    status_code = int(status_text)
    if status_code < 200 or status_code >= 300:
        raise RuntimeError(f"provider HTTP {status_code}: {body}")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        content = extract_responses_text_from_raw_body(body)
        if isinstance(content, str):
            return {"output_text": content}
        raise RuntimeError(f"provider returned invalid JSON: {body}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"provider returned non-object JSON: {data}")
    return data


def extract_responses_text(data: dict[str, Any]) -> str | None:
    output_text = data.get("output_text")
    if isinstance(output_text, str):
        return output_text
    output = data.get("output")
    if not isinstance(output, list):
        return None
    chunks: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "".join(chunks) if chunks else None


def extract_responses_text_from_raw_body(body: str) -> str | None:
    """Best-effort recovery for proxy responses with malformed JSON escaping."""
    start_token = '"text":"'
    start = body.find(start_token)
    if start == -1:
        return None
    start += len(start_token)
    end_candidates = [
        body.find('"}],"status"', start),
        body.find('"}]},"usage"', start),
        body.find('"}]}', start),
    ]
    end_candidates = [index for index in end_candidates if index != -1]
    if not end_candidates:
        return None
    raw_text = body[start : min(end_candidates)]
    try:
        return json.loads(f'"{raw_text}"')
    except json.JSONDecodeError:
        return raw_text.replace(r"\"", '"').replace(r"\\", "\\")


def parse_response_json(raw_text: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        data = parse_embedded_json_object(raw_text)
    return data if isinstance(data, dict) else None


def parse_embedded_json_object(raw_text: str) -> Any:
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(raw_text[start : end + 1])
    except json.JSONDecodeError:
        return None


def format_prompt_as_string(prompt: dict[str, Any]) -> str:
    system = str(prompt.get("system_prompt", "")).strip()
    user = str(prompt.get("user_prompt", "")).strip()
    if system and user:
        return f"System instructions:\n{system}\n\nUser prompt:\n{user}"
    return system or user


def truncate(text: str, limit: int | None) -> str:
    return text if limit is None else text[:limit]


def optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the standard LLM client.")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--no-json-mode", action="store_true")
    parser.add_argument("--system", default="You are a concise research assistant.")
    parser.add_argument("--user", default='Reply with JSON: {"ok": true, "message": "hello"}')
    args = parser.parse_args()

    try:
        llm = LLM(
            args.config,
            provider=args.provider,
            model=args.model,
            temperature=args.temperature,
            json_mode=False if args.no_json_mode else None,
        )
        print(llm.complete(args.system, args.user))
        return 0
    except Exception as exc:
        parser.exit(2, f"llm_client error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
