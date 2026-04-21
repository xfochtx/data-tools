import pandas as pd
import pickle
import time
from datetime import datetime
from osgeo import ogr
from .base import ArchivoBase
from .utils.helpers import ensure_folder, reorder_sheets
from .utils.config_export_excel import export_with_template

class Exportar(ArchivoBase):
  def pickle(self, objeto):
    ensure_folder(self.carpeta)
    with open(self.ruta_archivo, "wb") as archivo:
      pickle.dump(objeto, archivo)

  def excel(self, dataframe, sheet_name='Hoja1', path_template=None, index=False, _append=False, **kwargs):
    """
    Exporta un DataFrame a Excel.
    Si _append=True, se agrega al archivo existente (solo uso interno).
    """
    ensure_folder(self.carpeta)

    mode = 'a' if _append else 'w'

    if path_template:
      export_with_template(self.ruta_archivo, dataframe, sheet_name, path_template, append=_append)
    else:
      with pd.ExcelWriter(self.ruta_archivo, engine='openpyxl', mode=mode,
                          if_sheet_exists='replace' if _append else None) as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)

  def excel_multi_sheets(self, dataframes_dict, index=False, path_template=None, **kwargs):
    """
    Exporta varios DataFrames a un mismo Excel (sobrescribe desde cero),
    midiendo los tiempos de ejecución y mostrando información detallada.
    """
    ensure_folder(self.carpeta)

    start_time = time.time()
    start_dt = datetime.now().strftime("%H:%M:%S")
    print(f"\n🕒 [Inicio] Exportación de múltiples hojas iniciada a las {start_dt}")

    if self.ruta_archivo.exists():
      self.ruta_archivo.unlink()

    # --- Ordenar internamente por tamaño (de menor a mayor) ---
    sorted_items = sorted(
      dataframes_dict.items(),
      key=lambda item: len(item[1]) if hasattr(item[1], "__len__") else float("inf")
    )

    # --- Exportar excel con múltiples hojas ---
    for i, (sheet_name, df) in enumerate(sorted_items):
      sheet_start = time.time()
      print(f"  ➜ Exportando hoja '{sheet_name}' ({len(df)} filas)... ", end="", flush=True)

      self.excel(
        dataframe=df,
        sheet_name=sheet_name,
        path_template=path_template,
        index=index,
        _append=(i > 0),
        **kwargs
      )

      sheet_end = time.time()
      print(f"✔️  {sheet_end - sheet_start:.2f} segundos")

    # --- Reordenar hojas al orden original del diccionario ---
    start_reorder = datetime.now()
    print(f"[{start_reorder.strftime('%H:%M:%S')}] Iniciando reordenamiento de hojas...")
    reorder_sheets(self.ruta_archivo, list(dataframes_dict.keys()))

    end_reorder = datetime.now()
    elapsed_reorder = (end_reorder - start_reorder).total_seconds()
    print(f"[{end_reorder.strftime('%H:%M:%S')}] Reordenamiento completado ({elapsed_reorder:.2f} segundos)")

    # --- Mostrar tiempo total ---
    end_time = time.time()
    duration = end_time - start_time
    end_dt = datetime.now().strftime("%H:%M:%S")

    print(f"✅ [Fin] Exportación completada a las {end_dt}")
    print(f"⏱️  Duración total: {duration:.2f} segundos\n")

  def shapefile(self, gdf, columnas_hiperenlace=None):
    """
    Exporta el GeoDataFrame como Shapefile, permitiendo especificar una o varias columnas
    que se mantendrán como atributos (por ejemplo, hiperenlaces).

    Parámetros:
      gdf: GeoDataFrame a exportar.
      columnas_hiperenlace: str o lista de str, nombres de las columnas a mantener como atributos.
    """
    ensure_folder(self.carpeta)
    if columnas_hiperenlace is None:
      gdf.to_file(self.ruta_archivo, index=False)
    else:
      if isinstance(columnas_hiperenlace, str): # Asegura que sea lista
        columnas_hiperenlace = [columnas_hiperenlace]
      gdf.to_file(self.ruta_archivo, index=False, keep_attributes=columnas_hiperenlace)

  def kml(self, gdf, column_name=None):
    ensure_folder(self.carpeta)

    driver = ogr.GetDriverByName('KML')  # Obtener el driver KML
    data_source = driver.CreateDataSource(self.ruta_archivo)  # Crear el DataSource
    srs = None  # Definir el sistema de referencia si es necesario
    # Crear una nueva capa en el DataSource
    layer = data_source.CreateLayer(self.nombre_archivo, srs, ogr.wkbPoint)
    layer_defn = layer.GetLayerDefn()

    # Agregar atributos
    for field in gdf.columns:
      field_defn = ogr.FieldDefn(field, ogr.OFTString)
      layer.CreateField(field_defn)
    
    # Agregar geometrías
    for index, row in gdf.iterrows():
      feature = ogr.Feature(layer_defn)
      feature.SetGeometry(ogr.CreateGeometryFromWkt(row['geometry'].wkt))
      for field in gdf.columns:
        feature.SetField(field, str(row[field]))
      # Establecer el nombre visual
      if column_name and column_name in gdf.columns:
        feature.SetField('Name', str(row[column_name]))
      layer.CreateFeature(feature)
      feature = None
    # Cerrar el data source
    data_source = None
