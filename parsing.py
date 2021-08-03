import re
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, List

import pdfplumber as ppb
from pdfplumber.page import Page
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject, RectangleObject

from consts import months_es


def list_directory(dir: Path) -> Generator[Path]:
    for file in dir.iterdir():
        if file.exists() and file.is_file():
            return file


def get_title(table: List[str]) -> str:
    return str(table[0])


def parse_title(title: str) -> datetime:
    """
    Extracts year, month and day of the balance sheet title
    using regex
    """

    d, m, y = re.search(
        r'(?P<day>[\d]+) DE (?P<month>[A-Za-z]+) DE (?P<year>[\d]+)',
        title).groups()
    day = int(d.lstrip("0"))
    month = months_es[m] if m in months_es.keys() else ""
    year = int(y)
    parsed_date = datetime(year, month, day)

    return parsed_date


def get_table(file: Path) -> List[str]:
    with ppb.open(file) as pdf:
        p0: Page = pdf.pages[0]
        table = p0.extract_text().split("\n")

    return table


def clean_table(table: List[str], start: int = 2, end: int = -1) -> List[Any]:
    """
    Removes double spaces and empty strings, returning a
    cleaned list of lists
    """

    cleaned_table = [i.split("  ") for i in table[start:end]]
    cleaned_table = [list(filter(None, i)) for i in cleaned_table]

    return cleaned_table


def check_pdf(file: Path, target_directory: Path) -> Path:
    with file.open(mode="rb") as original:
        reader = PdfFileReader(original)
        page: PageObject = reader.getPage(0)

    # check if page is landscape oriented
    if not is_landscape(page.mediaBox):
        output = target_directory / f"{file.stem}_fixed{file.suffix}"
        # rotate page
        rotate_pdf(page, output)
        return output

    return file


def is_landscape(box: RectangleObject) -> bool:
    """
    Returns True if page orientation is 
    landscape else return False
    """

    if box.getUpperRight_x() - box.getUpperLeft_x() > box.getUpperRight_y() - box.getLowerRight_y():
        return True  # Landscape
    else:
        return False  # Portrait


def rotate_pdf(page: PageObject, output: Path) -> None:
    writer = PdfFileWriter()
    page.rotateClockwise(90)
    writer.addPage(page)

    with output.open() as fixed:
        writer.write(fixed)
