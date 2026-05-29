"""Functions to export/write data: Excel, Pickle, Shapefile, KML.

Usage:
    from dataport import writer

    writer.excel(Path("salida.xlsx"), df, sheet_name="Datos")
    writer.excel_multi_sheets(Path("consolidado.xlsx"), {"A": df1, "B": df2})
    writer.shapefile(Path("layer.shp"), gdf)
"""
import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .utils.config_export_excel import export_with_template
from .utils.helpers import ensure_folder, reorder_sheets


def excel(
  ruta: Path,
  df: pd.DataFrame,
  sheet_name: str = 'Hoja1',
  path_template: Path | None = None,
  index: bool = False,
  _append: bool = False,
  **kwargs,
):
  """Export a DataFrame to an Excel file.

  Args:
    ruta: Output path (.xlsx).
    df: DataFrame to export.
    sheet_name: Sheet name in the workbook.
    path_template: Optional .xlsx template to use as formatting base.
    index: Whether to write row indices.
    _append: Internal flag — if True, appends to an existing file.
    **kwargs: Passed through to df.to_excel().
  """
  ensure_folder(ruta.parent)

  mode = 'a' if _append else 'w'

  if path_template:
    export_with_template(ruta, df, sheet_name, path_template, append=_append)
  else:
    with pd.ExcelWriter(
      ruta,
      engine='openpyxl',
      mode=mode,
      if_sheet_exists='replace' if _append else None,
    ) as writer:
      df.to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)


def excel_multi_sheets(
  ruta: Path,
  dataframes: dict[str, pd.DataFrame],
  index: bool = False,
  path_template: Path | None = None,
  **kwargs,
):
  """Export multiple DataFrames to a single Excel file.

  Sheets are ordered by row count (smallest first) for performance,
  then reordered back to the original dict order.

  Args:
    ruta: Output path (.xlsx).
    dataframes: Dict mapping sheet names to DataFrames.
    index: Whether to write row indices.
    path_template: Optional .xlsx template for all sheets.
    **kwargs: Passed through to excel().
  """
  ensure_folder(ruta.parent)

  start_time = time.time()
  start_dt = datetime.now().strftime("%H:%M:%S")
  print(f"\n🕒 [Inicio] Exportación de múltiples hojas iniciada a las {start_dt}")

  if ruta.exists():
    ruta.unlink()

  sorted_items = sorted(
    dataframes.items(),
    key=lambda item: len(item[1]) if hasattr(item[1], "__len__") else float("inf"),
  )

  for i, (sheet_name, df) in enumerate(sorted_items):
    sheet_start = time.time()
    print(f"  ➜ Exportando hoja '{sheet_name}' ({len(df)} filas)... ", end="", flush=True)

    excel(ruta, df, sheet_name=sheet_name, path_template=path_template,
          index=index, _append=(i > 0), **kwargs)

    sheet_end = time.time()
    print(f"✔️  {sheet_end - sheet_start:.2f} segundos")

  reorder_sheets(ruta, list(dataframes.keys()))

  end_time = time.time()
  duration = end_time - start_time
  print(f"✅ [Fin] Exportación completada ({duration:.2f} segundos)")


def pickle_file(ruta: Path, obj: Any):
  """Export an object to a pickle file.

  Named pickle_file() to avoid shadowing the pickle module.

  Args:
    ruta: Output path (.pkl).
    obj: Object to serialize.
  """
  ensure_folder(ruta.parent)
  with open(ruta, 'wb') as f:
    pickle.dump(obj, f)


def shapefile(
  ruta: Path,
  gdf,
  columnas_hiperenlace: str | list[str] | None = None,
):
  """Export a GeoDataFrame to a Shapefile.

  Args:
    ruta: Output path (.shp).
    gdf: GeoDataFrame to export.
    columnas_hiperenlace: Column name(s) to keep as attributes (optional).
  """
  ensure_folder(ruta.parent)

  if columnas_hiperenlace is None:
    gdf.to_file(ruta, index=False)
  else:
    if isinstance(columnas_hiperenlace, str):
      columnas_hiperenlace = [columnas_hiperenlace]
    gdf.to_file(ruta, index=False, keep_attributes=columnas_hiperenlace)


def kml(ruta: Path, gdf, column_name: str | None = None):
  """Export a GeoDataFrame to KML.

  Args:
    ruta: Output path (.kml).
    gdf: GeoDataFrame to export.
    column_name: Column to use as the KML visual name (optional).
  """
  from osgeo import ogr

  ensure_folder(ruta.parent)

  driver = ogr.GetDriverByName('KML')
  data_source = driver.CreateDataSource(str(ruta))
  srs = None
  layer = data_source.CreateLayer(ruta.stem, srs, ogr.wkbPoint)
  layer_defn = layer.GetLayerDefn()

  for field in gdf.columns:
    field_defn = ogr.FieldDefn(field, ogr.OFTString)
    layer.CreateField(field_defn)

  for _, row in gdf.iterrows():
    feature = ogr.Feature(layer_defn)
    feature.SetGeometry(ogr.CreateGeometryFromWkt(row['geometry'].wkt))
    for field in gdf.columns:
      feature.SetField(field, str(row[field]))
    if column_name and column_name in gdf.columns:
      feature.SetField('Name', str(row[column_name]))
    layer.CreateFeature(feature)
    feature = None

  data_source = None
