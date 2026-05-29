"""Shared utility helpers."""
from pathlib import Path

def ensure_folder(path: Path):
  """Create directory tree if it doesn't exist."""
  path.mkdir(parents=True, exist_ok=True)
