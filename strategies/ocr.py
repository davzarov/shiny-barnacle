from pathlib import Path

import cv2
from consts import LOCAL_DIR
from wand.image import Image as WandImage


def create_empty_image(file: Path):
    output_image = LOCAL_DIR / (file.stem + '.jpg')

    if not output_image.exists():
        output_image.touch()

    return output_image


def pdf_to_img(file: Path, resolution: int = 300, compression_quality: int = 99):
    output_image = create_empty_image(file)

    with WandImage(filename=file, resolution=resolution) as img:
        img.compression_quality = compression_quality
        img.save(filename=output_image)

    return output_image


def mark_image(file: Path):
    img = cv2.imread(file)
    # transform to grayscale to reduce noise
    gray = cv2.cvtColor(src=img,
                        code=cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(src=gaussian,
                                   maxValue=255,
                                   adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   thresholdType=cv2.THRESH_BINARY_INV,
                                   blockSize=11,
                                   C=30)
    # dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT,
                                       ksize=(9, 9))
    dilate = cv2.dilate(src=thresh,
                        kernel=kernel,
                        iterations=4)
    # find contours, highlight text areas, and extract ROIs
    contours = cv2.findContours(image=dilate,
                                mode=cv2.RETR_EXTERNAL,
                                method=cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    line_items_coordinates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)

        if y >= 600 and x <= 1000:
            if area > 10000:
                image = cv2.rectangle(img=img,
                                      pt1=(x, y),
                                      pt2=(2200, y + h),
                                      color=(255, 0, 255),
                                      thickness=3)
                line_items_coordinates.append([(x, y), (2200, y + h)])

        if y >= 2400 and x <= 2000:
            image = cv2.rectangle(img=img,
                                  pt1=(x, y),
                                  pt2=(2200, y + h),
                                  color=(255, 0, 255),
                                  thickness=3)
            line_items_coordinates.append([(x, y), (2200, y + h)])

    return image, line_items_coordinates
