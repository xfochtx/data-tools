"""Export a GeoDataFrame to KML."""
from pathlib import Path

from ..utils.helpers import ensure_folder


def kml(path: Path, gdf, column_name: str | None = None):
  """Export a GeoDataFrame to KML.

  Args:
    path: Output .kml path.
    gdf: GeoDataFrame to export.
    column_name: Column to use as the KML visual name (optional).
  """
  from osgeo import ogr

  ensure_folder(path.parent)

  driver = ogr.GetDriverByName("KML")
  data_source = driver.CreateDataSource(str(path))
  srs = None
  layer = data_source.CreateLayer(path.stem, srs, ogr.wkbPoint)
  layer_defn = layer.GetLayerDefn()

  for field in gdf.columns:
    field_defn = ogr.FieldDefn(field, ogr.OFTString)
    layer.CreateField(field_defn)

  for _, row in gdf.iterrows():
    feature = ogr.Feature(layer_defn)
    feature.SetGeometry(ogr.CreateGeometryFromWkt(row["geometry"].wkt))
    for field in gdf.columns:
      feature.SetField(field, str(row[field]))
    if column_name and column_name in gdf.columns:
      feature.SetField("Name", str(row[column_name]))
    layer.CreateFeature(feature)
    feature = None

  data_source = None
