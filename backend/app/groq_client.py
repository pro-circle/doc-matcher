"""Thin Groq chat-completions client with key rotation and bounded backoff."""

from __future__ import annotations

import asyncio
import json
import random
import re
from typing import Any, Dict, List

import httpx

from .config import key_pool, settings

MAX_ATTEMPTS = 4


class GroqError(RuntimeError):
    pass


async def chat(
    task: str,
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> str:
    """Call Groq for a pipeline task, rotating keys on 429/5xx."""
    last_error: str = "unknown error"

    for attempt in range(MAX_ATTEMPTS):
        api_key = key_pool.key_for(task, attempt)
        payload: Dict[str, Any] = {
            "model": settings.groq_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{settings.groq_base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
        except httpx.HTTPError as exc:  # network failure -> retry on next key
            last_error = str(exc)
            await _sleep(attempt)
            continue

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"] or ""

        last_error = f"{response.status_code}: {response.text[:400]}"
        if response.status_code in (429,) or response.status_code >= 500:
            retry_after = response.headers.get("retry-after")
            await _sleep(attempt, float(retry_after) if retry_after else None)
            continue
        # 400/401/403 are terminal — the same request will fail again.
        raise GroqError(last_error)

    raise GroqError(f"Groq request failed after {MAX_ATTEMPTS} attempts — {last_error}")


async def chat_json(task: str, messages: List[Dict[str, str]], **kwargs: Any) -> Any:
    """Call Groq and parse the response as JSON, tolerating fenced output."""
    raw = await chat(task, messages, **kwargs)
    return parse_json(raw)


def parse_json(raw: str) -> Any:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = min(
            (index for index in (text.find("{"), text.find("[")) if index != -1),
            default=-1,
        )
        end = max(text.rfind("}"), text.rfind("]"))
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise GroqError("Model did not return valid JSON")


async def _sleep(attempt: int, retry_after: float | None = None) -> None:
    delay = retry_after if retry_after is not None else (2**attempt) * 0.6
    await asyncio.sleep(min(delay + random.uniform(0, 0.3), 20))
