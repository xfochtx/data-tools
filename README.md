# DataTools

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-3.0.0-orange)

## Descripción

**DataTools** es un paquete de Python que facilita la importación, exportación y procesamiento de datos en formatos **Excel**, **CSV**, **Pickle**, **PDF** y formatos geoespaciales.  
Está estructurado en módulos orientados a objetos para mayor flexibilidad y mantenibilidad.

## Módulos

### `dataport` — Importación y exportación

- Importar y exportar datos en Excel, CSV, Pickle y formatos geoespaciales.
- Personalización de formatos en exportación (fechas, alineación, anchos de columna).
- Uso de plantillas Excel para exportación avanzada.

### `processing` — Procesamiento de PDFs y de coordenadas espaciales

- `reestructurar_pdf`: Convierte páginas específicas de un PDF a imagen o las deja editables.
- `convertir_pdf_a_imagenes`: Convierte páginas específicas a imágenes PNG.
- `crear_pdf_de_imagenes`: Crea un PDF a partir de imágenes.
- `unir_pdfs`: Combina múltiples PDFs en uno solo.
- CoordinateProcessor: Clase para procesar coordenadas geoespaciales

## Instalación

### Instalación local desde el repositorio

```bash
pip install -e .
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

### Módulo `io`

```python
from dataport import Importar, Exportar

# Importar datos desde Excel
importador = Importar("datos", "archivo.xlsx")
df = importador.excel()

# Exportar datos a Excel
exportador = Exportar("datos", "archivo.xlsx")
exportador.excel(df, sheet_name="Hoja1")
```

### Módulo `processing`

```python
from processing.pdf import (
    reestructurar_pdf,
    convertir_pdf_a_imagenes,
    crear_pdf_de_imagenes,
    unir_pdfs
)

# Reestructurar: páginas editables y páginas como imagen
pdf_procesado = reestructurar_pdf(
    "documento.pdf",
    "output",
    "documento_procesado.pdf",
    [
        ((1, 10), "editable"),   # páginas 1-10 como editable
        ((11, 15), "imagen"),    # páginas 11-15 como imagen
    ]
)

# Combinar con otros PDFs si lo deseas
unir_pdfs([pdf_procesado, "anexos.pdf"], "resultado_final.pdf")
```

## Contribuciones

¿Te gustaría mejorar este paquete?  
¡Las contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request.

## Autor

- **Focht**  
  [fabian.chipana@unmsm.edu.pe](mailto:fabian.chipana@unmsm.edu.pe)
