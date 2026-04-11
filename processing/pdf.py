from pdf2image import convert_from_path
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from fpdf import FPDF
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

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

def comprimir_pdf(input_pdf, output_pdf, max_width=1500, quality=75, grayscale=True):
  """
  Comprime un PDF reduciendo tamaño de imágenes de forma segura.

  Args:
      input_pdf (Path | str): Ruta al PDF de entrada.
      output_pdf (Path | str): Ruta de salida.
      max_width (int): Ancho máximo de imágenes (px). Mantiene aspecto.
      quality (int): Calidad JPEG (1–100).
      grayscale (bool): Convertir imágenes a escala de grises.

  Returns:
      Path: Ruta al PDF comprimido.
  """
  input_pdf = Path(input_pdf)
  output_pdf = Path(output_pdf)
  output_pdf.parent.mkdir(parents=True, exist_ok=True)

  doc = fitz.open(str(input_pdf))

  procesadas = set()

  for page in doc:
    for img in page.get_images(full=True):
      xref = img[0]

      # Evitar reprocesar la misma imagen
      if xref in procesadas:
        continue
      procesadas.add(xref)

      try:
        pix = fitz.Pixmap(doc, xref)

        # Convertir a RGB si es necesario
        if pix.n >= 5:  # CMYK o alpha
          pix = fitz.Pixmap(fitz.csRGB, pix)

        img_bytes = pix.tobytes("png")
        pil_img = Image.open(io.BytesIO(img_bytes))

        # Escala de grises opcional
        if grayscale and pil_img.mode != "L":
          pil_img = pil_img.convert("L")

        # Redimensionar si es muy grande
        if pil_img.width > max_width:
          ratio = max_width / pil_img.width
          new_size = (
            int(pil_img.width * ratio),
            int(pil_img.height * ratio),
          )
          pil_img = pil_img.resize(new_size, Image.LANCZOS)

        # Elegir formato inteligentemente
        if pil_img.mode == "L" or pil_img.mode == "RGB":
          buf = io.BytesIO()
          pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
          new_bytes = buf.getvalue()
        else:
          buf = io.BytesIO()
          pil_img.save(buf, format="PNG", optimize=True)
          new_bytes = buf.getvalue()

        # ✅ Reemplazo seguro del stream
        doc.update_stream(xref, new_bytes)

      except Exception as e:
        print(f"  Warning: No se pudo comprimir imagen {xref}: {e}")

  # Guardado optimizado
  doc.save(
    str(output_pdf),
    garbage=4,       # limpia objetos no usados
    deflate=True,    # comprime streams
  )
  doc.close()

  # Métricas
  tamano_original = input_pdf.stat().st_size / (1024 * 1024)
  tamano_comprimido = output_pdf.stat().st_size / (1024 * 1024)

  reduccion = (
    (1 - tamano_comprimido / tamano_original) * 100
    if tamano_original > 0 else 0
  )

  print(f"PDF comprimido: {tamano_original:.2f} MB → {tamano_comprimido:.2f} MB ({reduccion:.1f}% reducción)")
  print(f"Guardado en: {output_pdf}")

  return output_pdf
