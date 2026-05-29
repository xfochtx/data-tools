"""Internal Excel export utilities — do not import directly.

Use ``writer.excel()`` or ``writer.excel_multi_sheets()`` instead.
"""
from .main import write, write_multi
from . import style

__all__ = ["write", "write_multi", "style"]
