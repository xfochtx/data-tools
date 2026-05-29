"""Export a GeoDataFrame to Shapefile."""
from pathlib import Path

from ..utils.helpers import ensure_folder


def shapefile(
  path: Path,
  gdf,
  link_columns: str | list[str] | None = None,
):
  """Export a GeoDataFrame to a Shapefile.

  Args:
    path: Output .shp path.
    gdf: GeoDataFrame to export.
    link_columns: Column name(s) to keep as attributes (optional).
  """
  ensure_folder(path.parent)

  if link_columns is None:
    gdf.to_file(path, index=False)
  else:
    if isinstance(link_columns, str):
      link_columns = [link_columns]
    gdf.to_file(path, index=False, keep_attributes=link_columns)
