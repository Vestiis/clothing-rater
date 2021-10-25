import base64
from typing import List, Optional, Union

from pydantic import BaseModel, validator

from src.interpreter import LabelCountry, LabelMaterial
from src.scorer import GlobalScore


class LabelMessage(BaseModel):
    user_id: str
    preferences: List[str]
    images: Optional[Union[List[str], List[bytes]]] = None
    images_urls: Optional[List[str]] = None
    images_labels: Optional[List[str]] = None

    @validator("images")
    def images_to_bytes(cls, images):
        if images is not None:
            return [
                base64.decodebytes(x.encode("utf8")) if isinstance(x, str) else x
                for x in images
            ]


class ScoreResponse(BaseModel):
    score: GlobalScore
    materials: List[LabelMaterial]
    country: LabelCountry
