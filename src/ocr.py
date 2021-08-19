from typing import List, Optional

from google.cloud import vision


class Ocr:
    def __init__(self):
        self.client_vision = vision.ImageAnnotatorClient()

    def __call__(
        self, image_url: Optional[str] = None, image_bytes: Optional[bytes] = None
    ):
        if image_url is not None:
            image = vision.Image()
            image.source.image_uri = image_url
        elif image_bytes is not None:
            image = vision.Image(content=image_bytes)
        else:
            raise Exception("image_url or image_bytes must be provided to perform ocr")
        return list(self.client_vision.text_detection(image=image).text_annotations)[
            0
        ].description


def get_ocr():
    return Ocr()
