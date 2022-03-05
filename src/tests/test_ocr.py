import pytest
import requests

from src.config import Config
from src.ocr import get_ocr


@pytest.mark.parametrize(
    "image_url", ["https://storage.googleapis.com/public-labels/IMG_9193.HEIC"],
)
def test_ocr_set_image_format_for_google_ocr(image_url: str):
    ocr = get_ocr()
    image = ocr.set_image_format_for_google_ocr(
        image=ocr.get_image_from_bytes(image_bytes=requests.get(image_url).content)
    )
    assert image.format == Config.Ocr.google_image_format
