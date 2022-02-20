import io

import pytest
import requests
from PIL import Image

from src.config import Config
from src.ocr import get_ocr


@pytest.mark.parametrize(
    "image_url", ["https://storage.googleapis.com/public-labels/IMG_9193.HEIC"],
)
def test_ocr_set_image_format_for_google_ocr(image_url: str):
    image_bytes = get_ocr().set_image_format_for_google_ocr(
        requests.get(image_url).content
    )
    image = Image.open(io.BytesIO(image_bytes))
    assert image.format == Config.Ocr.google_image_format
