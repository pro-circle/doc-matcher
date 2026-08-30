"""Environment configuration and the Groq API key pool."""

from __future__ import annotations

import itertools
import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    groq_keys: List[str] = field(default_factory=list)
    groq_model: str = "openai/gpt-oss-120b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    cors_origins: List[str] = field(default_factory=list)
    max_upload_bytes: int = 20 * 1024 * 1024

    @classmethod
    def load(cls) -> "Settings":
        keys = [
            os.getenv(f"GROQ_API_KEY_{index}", "").strip()
            for index in range(1, 5)
        ]
        keys = [key for key in keys if key]
        origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ] or ["*"]
        return cls(
            groq_keys=keys,
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            groq_base_url=os.getenv(
                "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
            ).rstrip("/"),
            cors_origins=origins,
            max_upload_bytes=int(float(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024),
        )


settings = Settings.load()


# Pipeline tasks, each pinned to its own key when four keys are configured.
TASKS = ("master_analysis", "child_analysis", "semantic_compare", "change_generation")


class KeyPool:
    """Assigns a key per task and round-robins on rate limits / upstream errors."""

    def __init__(self, keys: List[str]) -> None:
        self._keys = keys
        self._cycle = itertools.cycle(range(len(keys))) if keys else None

    @property
    def configured(self) -> bool:
        return bool(self._keys)

    def key_for(self, task: str, attempt: int = 0) -> str:
        if not self._keys:
            raise RuntimeError(
                "No Groq API keys configured. Set GROQ_API_KEY_1..4 in backend/.env"
            )
        base = TASKS.index(task) if task in TASKS else 0
        return self._keys[(base + attempt) % len(self._keys)]

    def size(self) -> int:
        return len(self._keys)


key_pool = KeyPool(settings.groq_keys)
