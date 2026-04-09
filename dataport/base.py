from pathlib import Path

class ArchivoBase:
  def __init__(self, carpeta, nombre_archivo):
    self.carpeta = Path(carpeta)
    self.nombre_archivo = nombre_archivo
    self.ruta_archivo = self.carpeta / self.nombre_archivo