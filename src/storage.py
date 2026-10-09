# src/storage.py
"""File I/O layer. Handles loading and saving reservations to JSON."""

import json
from pathlib import Path
from typing import List

from reservation import Reservation

# Resolve path relative to project root, not CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "reservations.json"


def load_reservations() -> List[Reservation]:
    """Load all reservations from disk. Returns empty list if file missing/empty."""
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        print(f"[warn] {DATA_FILE} is corrupted. Starting with empty list.")
        return []

    return [Reservation.from_dict(item) for item in raw]


def save_reservations(reservations: List[Reservation]) -> None:
    """Persist all reservations to disk as a JSON array."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [r.to_dict() for r in reservations],
            f,
            indent=2,
            ensure_ascii=False,
        )