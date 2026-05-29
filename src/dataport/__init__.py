"""Data import and export utilities.

Usage:
    from dataport import reader, writer

    df = reader.excel(Path("data.xlsx"))
    writer.excel(Path("out.xlsx"), df)
    writer.pickle(Path("data.pkl"), obj)
    writer.shapefile(Path("layer.shp"), gdf)
    writer.kml(Path("doc.kml"), gdf)
"""
from . import reader
from . import writer

__all__ = ["reader", "writer"]
