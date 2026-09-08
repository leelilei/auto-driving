"""Cache management, dry-run accounting, and attempt persistence for DARC-Route.

Per Proposal v4 & EXPERIMENT_GUIDE.md Section 10:
- Cache key contains:
  (input_text, prompt_hash, model_config_hash, draw_id, purpose)
  Draw ID isolation: "A", "B", "review", "A2", "A3".
  Draw IDs A, A2, A3 have distinct keys even with identical prompt and text.
- Never stores API keys in cache or config.
- Planning cache: (graph_hash, intent_tuple, solver_version).
- Supports dry-run (computes required calls, 0 API calls).
- Supports resume (skips already completed attempts).
- Tracks provider usage vs estimated token counts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def compute_call_key(
    input_text: str,
    prompt_text: str,
    model_config: dict[str, Any],
    draw_id: str,
    purpose: str = "exploratory",
) -> str:
    """Generate unambiguous hash key for an LLM attempt.

    Guarantees draw_id isolation (A vs A2 vs A3).
    Omits sensitive API keys.
    """
    # Safe model config representation (no api keys)
    safe_config = {
        "provider": model_config.get("provider", "unknown"),
        "model": model_config.get("model", "unknown"),
        "temperature": model_config.get("temperature", 0.0),
        "max_output_tokens": model_config.get("max_output_tokens", 1600),
        "omit_temperature": model_config.get("omit_temperature", False),
    }

    raw = {
        "text": input_text.strip(),
        "prompt": prompt_text.strip(),
        "config": safe_config,
        "draw_id": draw_id,
        "purpose": purpose,
    }
    dumped = json.dumps(raw, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


class LLMCacheManager:
    def __init__(self, cache_dir: Path | str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_index: dict[str, dict[str, Any]] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                self.memory_index = json.loads(index_file.read_text(encoding="utf-8"))
            except Exception:
                self.memory_index = {}

    def _save_index(self) -> None:
        index_file = self.cache_dir / "cache_index.json"
        index_file.write_text(json.dumps(self.memory_index, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, key: str) -> dict[str, Any] | None:
        """Lookup cached attempt by key."""
        if key in self.memory_index:
            entry = self.memory_index[key]
            # Verify file artifact exists
            rel_path = entry.get("file_path")
            if rel_path:
                full_path = self.cache_dir / rel_path
                if full_path.exists():
                    try:
                        return json.loads(full_path.read_text(encoding="utf-8"))
                    except Exception:
                        pass
            return entry.get("data")
        return None

    def put(
        self,
        key: str,
        attempt_record: dict[str, Any],
        draw_id: str,
        purpose: str,
    ) -> None:
        """Store attempt record in cache."""
        filename = f"{key}.json"
        file_path = self.cache_dir / filename
        file_path.write_text(json.dumps(attempt_record, indent=2, ensure_ascii=False), encoding="utf-8")

        self.memory_index[key] = {
            "key": key,
            "draw_id": draw_id,
            "purpose": purpose,
            "file_path": filename,
            "data": {
                "schema_valid": attempt_record.get("schema_valid", False),
                "raw_response": attempt_record.get("raw_response"),
                "parsed_intent": attempt_record.get("parsed_intent"),
                "telemetry": attempt_record.get("telemetry"),
            },
        }
        self._save_index()
