"""
Coordinate and CRS transformation utilities for Excel data processing.
"""
import math
import pandas as pd
from pyproj import Transformer
import geopandas as gpd
from shapely.geometry import Point

# ============================================================
# Coordinate Conversion (DMS <-> Decimal)
# ============================================================

class Coordinates:
  """
  Handles conversion between decimal coordinates and DMS (degrees, minutes, seconds).
  """

  def __init__(self, east, north):
    """
    Args:
      east: Easting coordinate (longitude) - can be decimal or DMS string
      north: Northing coordinate (latitude) - can be decimal or DMS string
    """
    self.east = east
    self.north = north

  @staticmethod
  def get_direction(coordinate: float, coord_type: str) -> str:
    """
    Returns the cardinal direction for a coordinate.
    
    Args:
      coordinate: The coordinate value
      coord_type: 'longitude' or 'latitude'
    
    Returns:
      'W' or 'E' for longitude, 'S' or 'N' for latitude
    """
    tolerance = 1e-6
    if coord_type == 'longitude':
      return 'W' if coordinate < -tolerance else 'E'
    if coord_type == 'latitude':
      return 'S' if coordinate < -tolerance else 'N'
    return 'N'  # Default fallback

  @staticmethod
  def decimal_to_dms(coordinate: float, coord_type: str) -> str | float:
    """
    Converts decimal degrees to DMS format.
    
    Args:
      coordinate: Decimal degree value
      coord_type: 'longitude' or 'latitude'
    
    Returns:
      String in format: "45° 30' 15.00'' N", or float('nan') if NaN input
    """
    if math.isnan(coordinate):
      return float('nan')

    degrees = int(coordinate)
    minutes_float = (abs(coordinate) - abs(degrees)) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    direction = Coordinates.get_direction(coordinate, coord_type)

    return f"{abs(degrees)}° {minutes}' {seconds:.2f}'' {direction}"

  @staticmethod
  def dms_to_decimal(coord_str: str | float) -> float:
    """
    Converts DMS string to decimal degrees.
    
    Args:
      coord_str: DMS string like "45° 30' 15.00'' N" or numeric value
    
    Returns:
      Decimal degrees as float
    """
    if isinstance(coord_str, str):
      parts = coord_str.split()
      degrees = float(parts[0].replace('°', ''))
      minutes = float(parts[1].replace("'", ''))
      seconds = float(parts[2].replace("''", ''))
      sign = -1 if coord_str.endswith(('W', 'S')) else 1

      return sign * (degrees + minutes / 60.0 + seconds / 3600.0)
    
    return coord_str  # Return as-is if already numeric

  def to_dms(self) -> tuple[str | float, str | float]:
    """
    Converts both east and north coordinates to DMS.
    
    Returns:
      Tuple of (east_dms, north_dms)
    """
    east_dms = Coordinates.decimal_to_dms(self.east, 'longitude')
    north_dms = Coordinates.decimal_to_dms(self.north, 'latitude')
    return east_dms, north_dms

  def to_decimal(self) -> tuple[float, float]:
    """
    Converts both east and north from DMS to decimal (if they are strings).
    
    Returns:
      Tuple of (east_decimal, north_decimal)
    """
    self.east = Coordinates.dms_to_decimal(self.east)
    self.north = Coordinates.dms_to_decimal(self.north)
    return self.east, self.north


# ============================================================
# CRS Transformer
# ============================================================

class CRSTransformer:
  """
  Handles coordinate reference system transformations using pyproj.
  """

  def __init__(self, source_epsg: str, target_epsg: str = "EPSG:4326"):
    """
    Args:
      source_epsg: Source CRS (e.g., "EPSG:32718")
      target_epsg: Target CRS (default: EPSG:4326 for geographic)
    """
    self.source_epsg = source_epsg
    self.target_epsg = target_epsg
    self.transformer = Transformer.from_crs(source_epsg, target_epsg, always_xy=True)

  def transform(self, east: float, north: float) -> tuple[float, float]:
    """
    Transforms a single point from source to target CRS.
    
    Returns:
      Tuple of (longitude, latitude) in target CRS
    """
    return self.transformer.transform(east, north)


# ============================================================
# DataFrame Processing
# ============================================================

class CoordinateProcessor:
  """
  Processes DataFrames with coordinate columns, applying transformations efficiently.
  """

  def __init__(self, dataframe: pd.DataFrame, col_east: str, col_north: str, col_epsg: str):
    """
    Args:
      dataframe: DataFrame with coordinate columns
      col_east: Column name for easting (X) coordinates
      col_north: Column name for northing (Y) coordinates
      col_epsg: Column name for EPSG codes
    """
    self.df = dataframe
    self.col_east = col_east
    self.col_north = col_north
    self.col_epsg = col_epsg

  def _create_transformer_cache(self) -> dict:
    """
    Creates a cache of CRSTransformers grouped by unique EPSG values.
    
    This is more efficient when most rows share the same EPSG.
    
    Returns:
      Dict mapping EPSG value to CRSTransformer instance
    """
    cache = {}
    unique_epsg = self.df[self.col_epsg].dropna().unique()

    for epsg in unique_epsg:
      epsg_str = str(epsg)
      if not epsg_str.startswith('EPSG:'):
        epsg_str = f"EPSG:{epsg_str}"
      cache[epsg] = CRSTransformer(epsg_str)

    return cache

  def metric_to_geographic(self, out_lon: str = 'Longitude', out_lat: str = 'Latitude') -> 'gpd.GeoDataFrame':
    """
    Converts metric coordinates to geographic decimal coordinates.
    
    Optimizes by grouping rows with the same EPSG and reusing transformers.
    Returns a GeoDataFrame with Point geometry.
    
    Args:
      out_lon: Output column name for longitude (default: 'Longitude')
      out_lat: Output column name for latitude (default: 'Latitude')
    
    Returns:
      GeoDataFrame with transformed coordinates and Point geometry
    """
    # Initialize output columns with existing values or NaN
    self.df[out_lon] = self.df.get(out_lon, pd.NA)
    self.df[out_lat] = self.df.get(out_lat, pd.NA)

    # Strategy: if all/majority share same EPSG, use group-based approach
    # Otherwise, fall back to row-by-row with cache
    unique_epsg_count = self.df[self.col_epsg].dropna().nunique()

    if unique_epsg_count == 1:
      # All rows share the same EPSG - most common case for Excel exports
      epsg_value = self.df[self.col_epsg].dropna().iloc[0]
      epsg_str = str(epsg_value)
      if not epsg_str.startswith('EPSG:'):
        epsg_str = f"EPSG:{epsg_str}"

      transformer = CRSTransformer(epsg_str)

      # Vectorized transformation (fastest)
      coords = transformer.transform(
        self.df[self.col_east].values,
        self.df[self.col_north].values
      )
      self.df[out_lon] = coords[0]
      self.df[out_lat] = coords[1]

    else:
      # Multiple EPSG values - use cache-based approach
      transformer_cache = self._create_transformer_cache()

      def transform_row(row):
        epsg = row.get(self.col_epsg)
        if pd.notnull(epsg) and epsg in transformer_cache:
          lon, lat = transformer_cache[epsg].transform(
            row[self.col_east], row[self.col_north]
          )
          return pd.Series([lon, lat], index=[out_lon, out_lat])
        return pd.Series([row.get(out_lon), row.get(out_lat)],
                       index=[out_lon, out_lat])

      result = self.df.apply(transform_row, axis=1, result_type='expand')
      self.df[out_lon] = result[out_lon]
      self.df[out_lat] = result[out_lat]

    # Convert to GeoDataFrame with Point geometry
    return self.to_geodataframe(out_lon, out_lat)

  def dms_to_decimal(self, col_lon: str = 'Longitude', col_lat: str = 'Latitude') -> pd.DataFrame:
    """
    Converts DMS-formatted coordinates to decimal degrees.
    
    Args:
      col_lon: Column name for longitude (default: 'Longitude')
      col_lat: Column name for latitude (default: 'Latitude')
    
    Returns:
      DataFrame with converted columns
    """
    self.df[col_lon] = self.df[col_lon].apply(Coordinates.dms_to_decimal)
    self.df[col_lat] = self.df[col_lat].apply(Coordinates.dms_to_decimal)
    return self.df

  def add_dms_columns(self, out_lon_dms: str = 'Lon_DMS', out_lat_dms: str = 'Lat_DMS', col_lon: str = 'Longitude', col_lat: str = 'Latitude') -> pd.DataFrame:
    """
    Adds new columns with DMS-formatted coordinates.
    
    Args:
      out_lon_dms: Output column name for longitude DMS (default: 'Lon_DMS')
      out_lat_dms: Output column name for latitude DMS (default: 'Lat_DMS')
      col_lon: Source longitude column (default: 'Longitude')
      col_lat: Source latitude column (default: 'Latitude')
    
    Returns:
      DataFrame with new DMS columns
    """
    self.df[out_lon_dms] = self.df[col_lon].apply(
      lambda x: Coordinates.decimal_to_dms(x, 'longitude')
    )
    self.df[out_lat_dms] = self.df[col_lat].apply(
      lambda x: Coordinates.decimal_to_dms(x, 'latitude')
    )
    return self.df

  def to_geodataframe(self, col_lon: str = 'Longitude', col_lat: str = 'Latitude') -> 'gpd.GeoDataFrame':
    """
    Converts DataFrame with coordinate columns to a Point GeoDataFrame.
    
    Args:
      col_lon: Column name for longitude (default: 'Longitude')
      col_lat: Column name for latitude (default: 'Latitude')
    
    Returns:
      GeoDataFrame with Point geometry
    """
    self.df['geometry'] = [
      Point(xy) for xy in zip(self.df[col_lon], self.df[col_lat])
    ]
    return gpd.GeoDataFrame(self.df, geometry='geometry')
