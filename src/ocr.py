import collections
import io
import logging
import math
from enum import Enum
from functools import cached_property, lru_cache
from typing import List, Optional

import magic
import pyheif
import requests
from google.cloud import vision
from PIL import Image
from pydantic import BaseModel

from src.config import Config
from src.exceptions import TextNotFound

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


class Vertex(BaseModel):
    x: float
    y: float


class GlobalOrientation:
    left = "left"
    right = "right"
    straight = "straight"


class OcrBoundingPoly(BaseModel):
    vertices: List[Vertex]

    class Config:
        # arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @cached_property
    def upper_left_reading_corner(self):
        return self.vertices[0]

    @cached_property
    def lower_right_reading_corner(self):
        return self.vertices[2]

    @cached_property
    def width(self):
        return abs(self.upper_left_reading_corner.x - self.lower_right_reading_corner.x)

    @cached_property
    def height(self):
        return abs(self.upper_left_reading_corner.y - self.lower_right_reading_corner.y)

    @cached_property
    def global_orientation(self):
        if self.width > self.height:
            return GlobalOrientation.straight
        elif self.upper_left_reading_corner.y < self.lower_right_reading_corner.y:
            return GlobalOrientation.right
        else:
            return GlobalOrientation.left


class GoogleImageFormat(str, Enum):
    JPEG = "JPEG"
    png = "png"


class Ocr:
    def __init__(
        self,
        pixels_per_image: int = 640 * 480,
        google_image_format: str = GoogleImageFormat.JPEG,
        # assume_image
    ):
        self.client_vision = vision.ImageAnnotatorClient()
        self.pixels_per_image = pixels_per_image
        self.google_image_format = google_image_format

    @property
    def google_image_extension(self):
        if self.google_image_format == "JPEG":
            return "jpg"
        elif self.google_image_format == "png":
            return "png"
        else:
            raise ValueError("Image format must be one of JPEG, png")

    def set_image_format_for_google_ocr(self, image: Image):
        if image.format is None or image.format != self.google_image_format:
            image_bytes = io.BytesIO()
            if self.google_image_format == GoogleImageFormat.JPEG:
                # JPEG does not support transparency so convert RGBA to RGB
                # https://stackoverflow.com/questions/48248405/cannot-write-mode-rgba-as-jpeg
                image = image.convert("RGB")
            image.save(image_bytes, format=self.google_image_format)
            image = self.get_image_from_bytes(image_bytes=image_bytes.getvalue())
        return image

    def set_quality(self, image: Image):
        width, height = image.size
        height_over_width = height / width
        new_width = int(math.sqrt(self.pixels_per_image / height_over_width))
        new_height = int(new_width * height_over_width)
        return image.resize((new_width, new_height), Image.ANTIALIAS)

    @staticmethod
    def crop_image_with_bounding_poly(
        image, image_bounding_polys: List[OcrBoundingPoly]
    ):
        vertices = [
            vertex
            for image_bounding_poly in image_bounding_polys
            for vertex in image_bounding_poly.vertices
        ]
        top = min(vertices, key=lambda vertex: vertex.y).y
        left = min(vertices, key=lambda vertex: vertex.x).x
        bottom = max(vertices, key=lambda vertex: vertex.y).y
        right = max(vertices, key=lambda vertex: vertex.x).x
        return image.crop((left, top, right, bottom))

    def rotate_image_with_bounding_polys(
        self, image, image_bounding_polys: List[OcrBoundingPoly]
    ):
        # bounding_polys are assumed to come from Google Vision and being ordered from
        # top of the label to bottom

        most_common_global_orientation, _ = collections.Counter(
            bounding_poly.global_orientation for bounding_poly in image_bounding_polys
        ).most_common(1)[0]
        if most_common_global_orientation == GlobalOrientation.straight:
            return image
        elif most_common_global_orientation == GlobalOrientation.right:
            return image.transpose(Image.ROTATE_90)
        elif most_common_global_orientation == GlobalOrientation.left:
            return image.transpose(Image.ROTATE_270)
        else:
            raise NotImplementedError

    def preprocess_with_bounding_polys(
        self, image, image_bounding_polys: List[OcrBoundingPoly]
    ):
        # crop
        image = self.crop_image_with_bounding_poly(
            image=image, image_bounding_polys=image_bounding_polys
        )
        # rotate
        image = self.rotate_image_with_bounding_polys(
            image=image, image_bounding_polys=image_bounding_polys
        )
        return image

    def preprocess(self, image: Image, image_bounding_polys=None):
        if image_bounding_polys is not None:
            image = self.preprocess_with_bounding_polys(
                image=image, image_bounding_polys=image_bounding_polys
            )
        image = self.set_image_format_for_google_ocr(image=image)
        image = self.set_quality(image)
        return image

    @staticmethod
    @lru_cache
    def get_image_from_bytes(image_bytes: List[bytes]):
        if "ISO Media" in magic.from_buffer(image_bytes):
            logger.warning(
                "Image is of ISO Media magic package file type, "
                "modifying it to another format"
            )
            heif_file = pyheif.read(image_bytes)
            return Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        return Image.open(io.BytesIO(image_bytes))

    def get_image_bytes(self, image: Image):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=self.google_image_format)
        return image_bytes.getvalue()

    def __call__(
        self,
        image_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_bounding_polys: Optional[List[OcrBoundingPoly]] = None,
    ):
        if image_url is not None:
            image_bytes = requests.get(image_url).content
        elif image_bytes is not None:
            pass
        else:
            raise Exception("image_url or image_bytes must be provided to perform ocr")

        image = self.get_image_from_bytes(image_bytes=image_bytes)
        preprocessed_image = self.preprocess(
            image=image, image_bounding_polys=image_bounding_polys
        )
        detections = list(
            self.client_vision.text_detection(
                image=vision.Image(content=self.get_image_bytes(preprocessed_image))
            ).text_annotations
        )
        if not detections:
            raise TextNotFound
        # x --> columns towards right
        # y --> lines towards down
        return (
            detections[0].description,
            [
                OcrBoundingPoly(
                    vertices=[
                        Vertex(
                            x=vertex.x / preprocessed_image.size[0] * image.size[0],
                            y=vertex.y / preprocessed_image.size[1] * image.size[1],
                        )
                        for vertex in detection.bounding_poly.vertices
                    ]
                )
                for detection in detections[1:]
            ],
        )


def get_ocr():
    return Ocr(
        pixels_per_image=Config.Ocr.pixels_per_image,
        google_image_format=Config.Ocr.google_image_format,
    )
