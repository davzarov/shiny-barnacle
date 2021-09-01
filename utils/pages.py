from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject, RectangleObject

from utils import make_file


def check_page_orientation(target_directory: Path, f: Path) -> Path:
    """checks file page orientation, if portrait returns a 90 deg
    rotated new file else returns original file"""

    # not sure about returning inside 'with' context manager, but
    # https://stackoverflow.com/questions/9885217/in-python-if-i-return-inside-a-with-block-will-the-file-still-close#9885287
    with f.open(mode="rb") as original:
        reader = PdfFileReader(original)
        page: PageObject = reader.getPage(0)

        if not is_landscape(page.mediaBox):
            page.rotateClockwise(90)
            writer = PdfFileWriter()
            writer.addPage(page)
            output = make_file(target_directory, f)
            with output.open(mode="wb") as fixed:
                writer.write(fixed)
            return output
        return f


def is_landscape(rect: RectangleObject) -> bool:
    """
    Returns True if page orientation is 
    landscape else return False
    """
    line_top = rect.getUpperRight_x() - rect.getUpperLeft_x()
    line_right = rect.getUpperRight_y() - rect.getLowerRight_y()

    if line_top > line_right:
        return True  # Landscape
    else:
        return False  # Portrait
