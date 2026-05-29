# DataTools

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-4.0.0-orange)

## Descripción

**DataTools** es un paquete de Python que facilita la importación, exportación y procesamiento de datos en formatos **Excel**, **CSV**, **Pickle**, **PDF** y formatos geoespaciales.

## Módulos

### `dataport` — Importación y exportación

Módulos funcionales (`reader`/`writer`) para leer y escribir datos:

- **reader**: Excel, CSV (auto-detección de encoding), Pickle y PDF (tablas, texto, páginas).
- **writer**: Excel (simple o multi-hoja con plantillas), Pickle, Shapefile y KML.
- Exportación con plantillas Excel para formato avanzado.

### `processing` — Procesamiento de PDFs y coordenadas espaciales

- `reestructurar_pdf`: Convierte páginas específicas de un PDF a imagen o las deja editables.
- `convertir_pdf_a_imagenes`: Convierte páginas específicas a imágenes PNG.
- `crear_pdf_de_imagenes`: Crea un PDF a partir de imágenes.
- `unir_pdfs`: Combina múltiples PDFs en uno solo.
- CoordinateProcessor: Clase para procesar coordenadas geoespaciales

## Instalación

### Instalación local desde el repositorio

```bash
pip install .
```

### Instalación desde GitHub

```bash
pip install git+https://github.com/xFochtX/Data-Tools --upgrade
```

> **Nota:**  
> Si necesitas trabajar con datos geoespaciales, instala manualmente la librería `osgeo` siguiendo la [documentación oficial](https://pypi.org/project/GDAL/).

## Requisitos

- Python 3.10+
- pandas, openpyxl, chardet
- pdfplumber, pdf2image, PyPDF2, fpdf
- geopandas (opcional)
- osgeo (opcional, para datos geoespaciales)

## Uso

### `dataport.reader` — Importar datos

```python
from dataport import reader

# Excel
df = reader.excel("datos/archivo.xlsx")

# CSV (encoding detectado automáticamente)
df = reader.csv("datos/archivo.csv")

# Tablas desde PDF
pages, tables = reader.pdf_tables("reporte.pdf")

# Texto desde PDF
pages, texts = reader.pdf_text("reporte.pdf")
```

### `dataport.writer` — Exportar datos

```python
from dataport import writer

# Excel simple
writer.excel("salida/reporte.xlsx", df, sheet_name="Datos")

# Excel multi-hoja con plantilla
writer.excel_multi_sheets(
    "salida/consolidado.xlsx",
    {"Áreas": df1, "Temas": df2},
    path_template="plantilla.xlsx",
)

# Shapefile
writer.shapefile("salida/capa.shp", gdf)
```

### `processing` — Procesar PDFs

```python
from processing.pdf import (
    reestructurar_pdf,
    convertir_pdf_a_imagenes,
    crear_pdf_de_imagenes,
    unir_pdfs,
)

pdf_procesado = reestructurar_pdf(
    "documento.pdf",
    "output",
    "documento_procesado.pdf",
    [
        ((1, 10), "editable"),   # páginas 1-10 como editable
        ((11, 15), "imagen"),    # páginas 11-15 como imagen
    ],
)

unir_pdfs([pdf_procesado, "anexos.pdf"], "resultado_final.pdf")
```

## Contribuciones

¿Te gustaría mejorar este paquete?  
¡Las contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request.

## Autor

- **Focht**  
  [fabian.chipana@unmsm.edu.pe](mailto:fabian.chipana@unmsm.edu.pe)
