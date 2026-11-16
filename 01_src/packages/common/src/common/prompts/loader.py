"""Prompt loader: reads versioned prompt files from 02_artifacts/prompts/.

Usage:
    from common.prompts.loader import load_prompt

    text, version, hash_ = load_prompt("search_sheets", "v1.0.0")
    # Pass version and hash_ to LlmRun for full traceability
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Resolves to <repo_root>/02_artifacts/prompts/ regardless of where the code runs
_PROMPTS_DIR = Path(__file__).parents[6] / "02_artifacts" / "prompts"


def load_prompt(name: str, version: str) -> tuple[str, str, str]:
    """Load a versioned prompt file and return its content, version and hash.

    Args:
        name:    Prompt folder name, e.g. ``"search_sheets"``.
        version: Semver string, e.g. ``"v1.0.0"``.

    Returns:
        Tuple of (text, version, sha256_hash[:12]).

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = _PROMPTS_DIR / name / f"{version}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {path}. "
            f"Available versions: {[p.name for p in path.parent.glob('v*.md')]}"
        )
    text = path.read_text(encoding="utf-8")
    hash_ = hashlib.sha256(text.encode()).hexdigest()[:12]
    return text, version, hash_
