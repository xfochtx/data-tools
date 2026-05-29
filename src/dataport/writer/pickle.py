"""Serialize an object to a pickle file."""
from pathlib import Path
from typing import Any
import pickle as _pickle

from ..utils.helpers import ensure_folder


def pickle(path: Path, obj: Any):
  """Serialize an object to a pickle file.

  Args:
    path: Output .pkl path.
    obj: Object to serialize.
  """
  ensure_folder(path.parent)
  with open(path, "wb") as f:
    _pickle.dump(obj, f)
