"""Functions to read/import data files: Excel, CSV, Pickle, PDF.

Usage:
    from dataport import reader

    df = reader.excel(Path("datos.xlsx"))
    df = reader.csv(Path("datos.csv"))
    obj = reader.pickle(Path("data.pkl"))
    pages, tables = reader.pdf_tables(Path("reporte.pdf"))
"""
from pathlib import Path
from typing import Any
import chardet
import pandas as pd
import pdfplumber
import pickle as _pickle


def excel(path: Path, **kwargs) -> pd.DataFrame:
  """Read an Excel file into a DataFrame.

  Args:
    path: Path to the .xlsx or .xls file.
    **kwargs: Passed through to pd.read_excel().
  """
  return pd.read_excel(path, **kwargs)


def csv(path: Path, **kwargs) -> pd.DataFrame:
  """Read a CSV file with auto-encoding detection.

  If no encoding is specified, detects it from the first 50 KB
  using chardet and defaults to utf-8.

  Args:
    path: Path to the .csv file.
    **kwargs: Passed through to pd.read_csv().
  """
  if 'encoding' not in kwargs:
    with open(path, 'rb') as f:
      result = chardet.detect(f.read(50000))
      kwargs['encoding'] = result['encoding'] or 'utf-8'
  return pd.read_csv(path, **kwargs)


def pdf_tables(
  path: Path,
  pages: str | list[int] = 'all',
  table_settings: dict | None = None,
) -> tuple[list[int], list[pd.DataFrame]]:
  """Extract tables from a PDF.

  Args:
    path: Path to the .pdf file.
    pages: 'all' or list of page numbers (1-based).
    table_settings: pdfplumber table extraction options.

  Returns:
    Tuple of (page_numbers, list_of_DataFrames).
  """
  page_numbers: list[int] = []
  tables: list[pd.DataFrame] = []

  with pdfplumber.open(path) as pdf:
    pdf_pages = pdf.pages if pages == 'all' else [pdf.pages[p - 1] for p in pages]

    for page in pdf_pages:
      extracted = page.extract_tables(table_settings=table_settings)
      for table_data in extracted:
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
        page_numbers.append(page.page_number)
        tables.append(df)

  return page_numbers, tables


def pdf_text(
  path: Path,
  pages: str | list[int] = 'all',
) -> tuple[list[int], list[str]]:
  """Extract text from a PDF.

  Args:
    path: Path to the .pdf file.
    pages: 'all' or list of page numbers (1-based).

  Returns:
    Tuple of (page_numbers, list_of_text_strings).
  """
  page_numbers: list[int] = []
  texts: list[str] = []

  with pdfplumber.open(path) as pdf:
    pdf_pages = pdf.pages if pages == 'all' else [pdf.pages[p - 1] for p in pages]

    for page in pdf_pages:
      page_numbers.append(page.page_number)
      texts.append(page.extract_text())

  return page_numbers, texts


def pdf_pages(
  path: Path,
  pages: str | list[int] = 'all',
) -> tuple[list[int], list]:
  """Extract raw pdfplumber Page objects from a PDF.

  Args:
    path: Path to the .pdf file.
    pages: 'all' or list of page numbers (1-based).

  Returns:
    Tuple of (page_numbers, list_of_Page_objects).
  """
  page_numbers: list[int] = []
  raw_pages: list = []

  with pdfplumber.open(path) as pdf:
    pdf_pages = pdf.pages if pages == 'all' else [pdf.pages[p - 1] for p in pages]

    for page in pdf_pages:
      page_numbers.append(page.page_number)
      raw_pages.append(page)

  return page_numbers, raw_pages


def pickle(path: Path) -> Any:
  """Read data from a pickle file.

  Named ``pickle()`` to mirror ``writer.pickle()``.

  Args:
    path: Path to the .pkl file.
  """
  with open(path, "rb") as f:
    return _pickle.load(f)
