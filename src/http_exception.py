from typing import Union

from fastapi import HTTPException, status

from src.exceptions import (
    CountryNotFound,
    MaterialNotFound,
    MissingMaterialPercentage,
    MultipleLabelErrors,
    TextNotFound,
)


class HttpLabelException(HTTPException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(
        self,
        exception: Union[
            MaterialNotFound,
            CountryNotFound,
            TextNotFound,
            MissingMaterialPercentage,
            MultipleLabelErrors,
        ],
    ):
        super().__init__(
            detail={
                "error": str(exception),
                "label": getattr(exception, "label", None),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
