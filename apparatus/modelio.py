from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from apparatus.canonical import compact_json, sha256_bytes
from apparatus.constants import CONTEXT_TOKENS, RESPONSE_RESERVE


@dataclass(frozen=True)
class TokenReceipt:
    prompt_tokens: int
    rendered_prompt_sha256: str
    rendered_prompt_size_bytes: int
    headroom_after_reserve: int
    fits: bool
    rendered_prompt: str
    response_reserve_tokens: int = RESPONSE_RESERVE

    def as_dict(self) -> dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "rendered_prompt_sha256": self.rendered_prompt_sha256,
            "rendered_prompt_size_bytes": self.rendered_prompt_size_bytes,
            "context_tokens": CONTEXT_TOKENS,
            "response_reserve_tokens": self.response_reserve_tokens,
            "headroom_after_reserve": self.headroom_after_reserve,
            "fits": self.fits,
        }


class ParentTokenEndpoint:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.apply_calls = 0
        self.tokenize_calls = 0

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(self.base_url + path, data=compact_json(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=120) as response:
            value = json.loads(response.read())
        if not isinstance(value, dict):
            raise ValueError(f"endpoint returned non-object for {path}")
        return value

    def count(self, messages: list[dict[str, Any]], kwargs: dict[str, Any], reserve: int = RESPONSE_RESERVE) -> TokenReceipt:
        applied = self._post("/apply-template", {"messages": messages, "add_generation_prompt": True, "chat_template_kwargs": kwargs})
        self.apply_calls += 1
        prompt = applied.get("prompt")
        if not isinstance(prompt, str):
            raise ValueError("apply-template response lacks prompt")
        tokenized = self._post("/tokenize", {"content": prompt, "add_special": False, "parse_special": True})
        self.tokenize_calls += 1
        tokens = tokenized.get("tokens")
        if not isinstance(tokens, list):
            raise ValueError("tokenize response lacks token list")
        count = len(tokens)
        raw = prompt.encode("utf-8")
        headroom = CONTEXT_TOKENS - reserve - count
        return TokenReceipt(count, sha256_bytes(raw), len(raw), headroom, headroom >= 0, prompt, reserve)

    def count_text(self, content: str) -> int:
        tokenized = self._post("/tokenize", {"content": content, "add_special": False, "parse_special": True})
        self.tokenize_calls += 1
        tokens = tokenized.get("tokens")
        if not isinstance(tokens, list):
            raise ValueError("tokenize response lacks token list")
        return len(tokens)


@dataclass(frozen=True)
class HttpRecord:
    status_code: int
    headers: dict[str, str]
    body: bytes
    duration_ms: int
    transport_error: str | None

    @property
    def success(self) -> bool:
        return self.transport_error is None and 200 <= self.status_code < 300


def http(request: urllib.request.Request, timeout_seconds: int = 900) -> HttpRecord:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return HttpRecord(int(response.status), {k.lower(): v for k, v in response.headers.items()}, response.read(), round((time.perf_counter() - started) * 1000), None)
    except urllib.error.HTTPError as exc:
        return HttpRecord(int(exc.code), {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}, exc.read(), round((time.perf_counter() - started) * 1000), None)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return HttpRecord(0, {}, b"", round((time.perf_counter() - started) * 1000), f"{type(exc).__name__}: {exc}")


def get_json(base_url: str, path: str) -> dict[str, Any]:
    response = http(urllib.request.Request(base_url.rstrip("/") + path, method="GET"), 60)
    if not response.success:
        raise RuntimeError(f"GET {path} failed: {response.status_code} {response.transport_error}")
    value = json.loads(response.body)
    if not isinstance(value, dict):
        raise RuntimeError(f"GET {path} returned non-object")
    return value


def post_chat(base_url: str, body: bytes) -> HttpRecord:
    return http(urllib.request.Request(base_url.rstrip("/") + "/v1/chat/completions", data=body, method="POST", headers={"Content-Type": "application/json"}))
