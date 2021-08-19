import base64
from typing import Optional, Union

from pydantic import BaseModel, validator


class ScoreMessage(BaseModel):
    image_bytes: Optional[Union[str, bytes]] = None
    image_url: Optional[str] = None
    image_label: Optional[str] = None

    @validator("image_bytes")
    def image_to_bytes(cls, image_bytes):
        if image_bytes is not None and isinstance(image_bytes, str):
            # cast string to bytes in base 2
            return base64.decodebytes(image_bytes.encode("utf8"))
        return image_bytes


class ScoreResponse(BaseModel):
    score: float
