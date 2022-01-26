import io
import logging
import math
import tempfile
from typing import List, Optional

import magic
import pyheif
import requests
from google.cloud import vision
from PIL import Image

from src.config import Config
from src.exceptions import TextNotFound

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


class Ocr:
    def __init__(self, pixels_per_image: int = 640 * 480):
        self.client_vision = vision.ImageAnnotatorClient()
        self.pixels_per_image = pixels_per_image

    @staticmethod
    def set_image_format_for_google_ocr(image_bytes: List[bytes]):
        # if file is of HEIC format then convert it to jpeg
        if "ISO Media" in magic.from_buffer(image_bytes):
            logger.warning(
                "Image is of ISO Media magic package file type, "
                "modifying it to another format"
            )
            tmp_file = tempfile.NamedTemporaryFile().name
            heif_file = pyheif.read(image_bytes)
            Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            ).save(f"{tmp_file}.jpg", "JPEG")
            image_bytes = open(f"{tmp_file}.jpg", "rb").read()
        return image_bytes

    def set_quality(self, image_bytes: List[bytes]):
        image = Image.open(io.BytesIO(image_bytes))
        height_over_width = image.size[1] / image.size[0]
        new_width = int(math.sqrt(self.pixels_per_image / height_over_width))
        new_height = int(new_width * height_over_width)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="png")
        return image_bytes.getvalue()

    def preprocess(self, image_bytes: List[bytes]):
        image_bytes = self.set_image_format_for_google_ocr(image_bytes=image_bytes)
        image_bytes = self.set_quality(image_bytes)
        return image_bytes

    def __call__(
        self, image_url: Optional[str] = None, image_bytes: Optional[bytes] = None
    ):
        if image_url is not None:
            image_bytes = requests.get(image_url).content
        elif image_bytes is not None:
            pass
        else:
            raise Exception("image_url or image_bytes must be provided to perform ocr")
        image_bytes = self.preprocess(image_bytes=image_bytes)
        image = vision.Image(content=image_bytes)
        detections = list(
            self.client_vision.text_detection(image=image).text_annotations
        )
        if not detections:
            raise TextNotFound
        return detections[0].description


def get_ocr():
    return Ocr(pixels_per_image=Config.Ocr.pixels_per_image)
