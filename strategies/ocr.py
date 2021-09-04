from pathlib import Path

from utils import make_file
from wand.image import Image as WandImage


def pdf_to_img(destination: Path, file: Path, resolution: int = 300, compression_quality: int = 99) -> Path:
    output_image = make_file(destination, file, ".jpg")

    with WandImage(filename=file, resolution=resolution) as img:
        img.compression_quality = compression_quality
        img.save(filename=output_image)

    return output_image
