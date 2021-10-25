import io
from typing import List, Optional

from google.cloud import vision
from PIL import Image

from src.exceptions import TextNotFound


class Ocr:
    def __init__(self, width: int = 1500, height: int = 1500):
        self.client_vision = vision.ImageAnnotatorClient()
        self.width = width
        self.height = height

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
            image = vision.Image()
            image.source.image_uri = image_url
        elif image_bytes is not None:
            # image_bytes = self.set_quality(image_bytes)
            image = vision.Image(content=image_bytes)
        else:
            raise Exception("image_url or image_bytes must be provided to perform ocr")
        detections = list(
            self.client_vision.text_detection(image=image).text_annotations
        )
        if not detections:
            raise TextNotFound
        return detections[0].description


def get_ocr():
    return Ocr()
