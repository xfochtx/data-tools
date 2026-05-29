"""Export functions: Excel, Pickle, Shapefile, KML, PDF.

Usage:
    from dataport import writer

    writer.excel(Path("out.xlsx"), df)
    writer.excel_multi_sheets(Path("out.xlsx"), {"A": df1, "B": df2})
    writer.pickle(Path("data.pkl"), obj)
    writer.shapefile(Path("layer.shp"), gdf)
    writer.kml(Path("doc.kml"), gdf)
"""
from pathlib import Path

from . import _excel
from .shapefile import shapefile
from .kml import kml
from .pickle import pickle

__all__ = [
  "excel", "excel_multi_sheets",
  "pickle", "shapefile", "kml",
]


# ── Excel ───────────────────────────────────────────────────────

def excel(path: Path, df, sheet_name: str = "Sheet1", template_path: Path | None = None, index: bool = False):
  """Export a DataFrame to an Excel file (single sheet).

  Args:
    path: Output .xlsx path.
    df: DataFrame to export.
    sheet_name: Sheet name in the workbook.
    template_path: Optional .xlsx template to use as formatting base.
    index: Whether to write row indices.
  """
  _excel.write(path, df, sheet_name=sheet_name, template_path=template_path, index=index)


def excel_multi_sheets(path: Path, dataframes: dict[str, object], index: bool = False, template_path: Path | None = None):
  """Export multiple DataFrames to a single Excel file.

  Args:
    path: Output .xlsx path.
    dataframes: Dict mapping sheet names to DataFrames.
    index: Whether to write row indices.
    template_path: Optional .xlsx template for all sheets.
  """
  _excel.write_multi(path, dataframes, index=index, template_path=template_path)
