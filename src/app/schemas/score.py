import base64
from typing import List, Optional, Union

from pydantic import BaseModel, ValidationError, validator

from src.interpreter import LabelCountry, LabelMaterial
from src.scorer import GlobalScore


class LabelMessageNoImageSourceError(Exception):
    def __str__(self):
        return (
            "At least one of 'images_labels' or 'images_urls' or 'images' "
            "fields must be provided"
        )


class LabelMessage(BaseModel):
    user_id: str
    preferences: List[str]
    images: Optional[Union[List[str], List[bytes]]] = None
    images_urls: Optional[List[str]] = None
    images_labels: Optional[List[str]] = None

    @validator("images_labels")
    def assert_at_least_one_image_source(cls, images_labels, values, **kwargs):
        if images_labels is not None:
            return images_labels
        elif values["images"] is not None:
            return images_labels
        elif values["images_urls"] is not None:
            return images_labels
        else:
            raise LabelMessageNoImageSourceError

    @validator("images")
    def images_to_bytes(cls, images):
        if images is not None:
            return [
                base64.decodebytes(x.encode("utf8")) if isinstance(x, str) else x
                for x in images
            ]


class ScoreResponse(BaseModel):
    label: str
    score: GlobalScore
    materials: List[LabelMaterial]
    country: LabelCountry
