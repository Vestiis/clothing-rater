import base64
from typing import List, Optional, Union

from pydantic import BaseModel, validator


class LabelMessage(BaseModel):
    images: Optional[Union[List[str], List[bytes]]] = None
    images_urls: Optional[str] = None
    images_labels: Optional[str] = None

    @validator("images")
    def images_to_bytes(cls, images):
        if images is not None:
            return [
                base64.decodebytes(x.encode("utf8")) if isinstance(x, str) else x
                for x in images
            ]


class ScoreResponse(BaseModel):
    score: float
