from pdf2image import convert_from_path
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from fpdf import FPDF
from pathlib import Path

def convertir_pdf_a_imagenes(pdf_path, output_folder, paginas_a_convertir, dpi=300):
  """Convierte páginas específicas de un PDF en imágenes PNG."""
  pages = convert_from_path(pdf_path, dpi)
  image_paths = []

  temp_folder = output_folder / "Temp"
  temp_folder.mkdir(parents=True, exist_ok=True)  # Crear carpeta si no existe

  for i in paginas_a_convertir:
    image_path = temp_folder / f"Página {i + 1}.png"
    pages[i].save(image_path, "PNG")
    image_paths.append(image_path)

  return image_paths

def crear_pdf_de_imagenes(image_paths, output_pdf, tamaño=(210, 297)):
  """Crea un PDF a partir de una lista de imágenes (A4 por defecto)."""
  pdf = FPDF()
  for image_path in image_paths:
    pdf.add_page()
    pdf.image(str(image_path), x=0, y=0, w=tamaño[0], h=tamaño[1])
  pdf.output(str(output_pdf))

def crear_pdf_de_editables(pdf_path, output_pdf, paginas_a_convertir):
  """Crea un PDF con las páginas seleccionadas como editables."""
  reader = PdfReader(str(pdf_path))
  writer = PdfWriter()
  for i in paginas_a_convertir:
    writer.add_page(reader.pages[i])
  with open(str(output_pdf), "wb") as f:
    writer.write(f)

def unir_pdfs(lista_pdfs, ruta_salida, verbose=True):
  """
  Une varios archivos PDF en un solo PDF.

  Args:
      lista_pdfs (list[Path | str]): Lista de PDFs a unir.
      ruta_salida (Path | str): Ruta donde se guardará el PDF combinado.
      verbose (bool): Si True, imprime la ruta final del PDF.
  """
  lista_pdfs = [Path(p) for p in lista_pdfs]
  ruta_salida = Path(ruta_salida)
  ruta_salida.parent.mkdir(parents=True, exist_ok=True)

  for pdf in lista_pdfs:
    if not pdf.is_file():
      raise FileNotFoundError(f"El archivo {pdf} no existe.")

  # Usamos context manager para cerrar automáticamente
  with PdfMerger() as merger:
    for pdf in lista_pdfs:
      merger.append(str(pdf))
    merger.write(str(ruta_salida))

  if verbose:
    print(f"PDF combinado guardado en: {ruta_salida}")

def reestructurar_pdf(pdf_entrada, output_folder, name_pdf_output, rangos_a_convertir, dpi=300, tamaño_a4=(210, 297)):
  """
  Procesa páginas de un PDF: convierte partes a imagen, partes quedan editables.

  Args:
    pdf_entrada (Path | str): Ruta al PDF de entrada.
    output_folder (Path | str): Carpeta para archivos temporales.
    rangos_a_convertir (list[tuple]): Lista de tuplas ((inicio, fin), tipo).
                                      tipo = "imagen" o "editable"
    dpi (int): Resolución para conversión a imagen (default 300).
    tamaño_a4 (tuple): Tamaño de página en mm (default A4).

  Returns:
    Path: Ruta al PDF reestructurado.
  """
  pdf_entrada = Path(pdf_entrada)
  output_folder = Path(output_folder)
  output_folder.mkdir(parents=True, exist_ok=True)

  pdfs_temporales = []

  for idx, (rango, tipo) in enumerate(rangos_a_convertir):
    start, end = rango
    indices_rango = list(range(start - 1, end))

    if tipo == "imagen":
      imagenes = convertir_pdf_a_imagenes(pdf_entrada, output_folder, indices_rango, dpi)
      pdf_temp = output_folder / f"temp_imagen_{idx + 1}.pdf"
      crear_pdf_de_imagenes(imagenes, pdf_temp, tamaño_a4)
      pdfs_temporales.append(pdf_temp)

    elif tipo == "editable":
      pdf_temp = output_folder / f"temp_editable_{idx + 1}.pdf"
      crear_pdf_de_editables(pdf_entrada, pdf_temp, indices_rango)
      pdfs_temporales.append(pdf_temp)

  # Combinar todos los fragmentos en un solo PDF
  pdf_reestructurado = output_folder / name_pdf_output
  unir_pdfs(pdfs_temporales, pdf_reestructurado, verbose=False)

  # Limpiar temporales
  for temp in pdfs_temporales:
    temp.unlink()

  print(f"PDF reestructurado guardado en: {pdf_reestructurado}")
  return pdf_reestructurado
