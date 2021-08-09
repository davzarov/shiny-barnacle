from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject, RectangleObject


def check_page_orientation(file: Path, target_directory: Path) -> Path:
    with file.open(mode="rb") as original:
        reader = PdfFileReader(original)
        page: PageObject = reader.getPage(0)

    if not is_landscape(page.mediaBox):
        name = file.stem  # stem -> name
        ext = file.suffix  # suffix -> extension
        output = target_directory / f"{name}_fixed{ext}"
        rotate_page(page, output)
        return output

    return file


def is_landscape(rect: RectangleObject) -> bool:
    """
    Returns True if page orientation is 
    landscape else return False
    """

    if rect.getUpperRight_x() - rect.getUpperLeft_x() > rect.getUpperRight_y() - rect.getLowerRight_y():
        return True  # Landscape
    else:
        return False  # Portrait


def rotate_page(page: PageObject, output: Path) -> None:
    writer = PdfFileWriter()
    page.rotateClockwise(90)
    writer.addPage(page)

    with output.open(mode="wb") as fixed:
        writer.write(fixed)
