"""Data import and export utilities.

Usage:
from . import reader, writer

    df = reader.excel(Path("datos.xlsx"))
    writer.excel(Path("salida.xlsx"), df)
"""
from dataport import reader, writer

__all__ = ["reader", "writer"]
