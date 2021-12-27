import io
import tempfile
from typing import List, Optional

import magic
import pyheif
import requests
from google.cloud import vision
from PIL import Image

from src.exceptions import TextNotFound


class Ocr:
    def __init__(self, width: int = 1500, height: int = 1500):
        self.client_vision = vision.ImageAnnotatorClient()
        self.width = width
        self.height = height

    @staticmethod
    def set_format_for_google_ocr(image_bytes: List[bytes]):
        # if file is of HEIC format then convert it to jpeg
        if magic.from_buffer(image_bytes) == "ISO Media":
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
        image = image.resize((self.width, self.height), Image.ANTIALIAS)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="png")
        return image_bytes.getvalue()

    def __call__(
        self, image_url: Optional[str] = None, image_bytes: Optional[bytes] = None
    ):
        if image_url is not None:
            image_bytes = requests.get(image_url).content
            # image = vision.Image()
            # image.source.image_uri = image_url
        # elif image_bytes is not None:
        elif image_bytes is not None:
            pass
        else:
            raise Exception("image_url or image_bytes must be provided to perform ocr")
        image_bytes = self.set_format_for_google_ocr(image_bytes)
        image = vision.Image(content=image_bytes)
        detections = list(
            self.client_vision.text_detection(image=image).text_annotations
        )
        if not detections:
            raise TextNotFound
        return detections[0].description


def get_ocr():
    return Ocr()
