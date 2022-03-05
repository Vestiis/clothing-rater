import logging
import sys
from typing import Optional

import requests
from fastapi import APIRouter, Body, Depends, HTTPException, status

from src.app.crud.score import ocr_and_compute_images_score
from src.app.schemas.score import LabelMessage, ScoreResponse
from src.config import Config
from src.exceptions import (
    CountryNotFound,
    MaterialNotFound,
    MissingMaterialPercentage,
    MultipleLabelErrors,
    TextNotFound,
)
from src.interpreter import Interpreter, get_interpreter
from src.ocr import Ocr, get_ocr
from src.scorer import Criteria

router = APIRouter()
logger = logging.getLogger(__name__)
# prevent compute score function from being called more than twice
sys.setrecursionlimit(100)


class RouteType:
    post_compute_score = "/post_compute_score"


def raise_error(exception: Exception, label: Optional[str] = None):
    if (
        isinstance(exception, MaterialNotFound)
        or isinstance(exception, CountryNotFound)
        or isinstance(exception, TextNotFound)
        or isinstance(exception, MissingMaterialPercentage)
        or isinstance(exception, MultipleLabelErrors)
    ):
        raise HTTPException(
            detail={"error": str(exception), "label": label},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    else:
        raise HTTPException(
            detail=str(exception), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post(RouteType.post_compute_score, response_model=ScoreResponse)
def post_compute_score(
    *,
    score_message: LabelMessage = Body(..., embed=False),
    ocr: Ocr = Depends(get_ocr),
    interpreter: Interpreter = Depends(get_interpreter),
    # credentials: HTTPAuthorizationCredentials = Security(security)
    # would this work to have the uuid that would allow me to retrieve
    # info about the user?
):
    label = None
    try:
        images_bytes = []
        if score_message.images_urls is not None:
            images_bytes += [
                requests.get(image_url).content
                for image_url in score_message.images_urls
            ]
        if score_message.images is not None:
            images_bytes += score_message.images

        clothing_score, materials, country, label = ocr_and_compute_images_score(
            interpreter=interpreter,
            ocr=ocr,
            environment_ranking=score_message.preferences.index(Criteria.environment)
            + 1,
            societal_ranking=score_message.preferences.index(Criteria.societal) + 1,
            animal_ranking=score_message.preferences.index(Criteria.animal) + 1,
            health_ranking=score_message.preferences.index(Criteria.health) + 1,
            pre_known_labels=score_message.images_labels,
            images_bytes=images_bytes,
            retry_with_google_bounding_polys=Config.ComputeScore.retry_with_google_bounding_polys,
            return_found_elements=True,
        )
    except (
        MaterialNotFound,
        CountryNotFound,
        TextNotFound,
        MissingMaterialPercentage,
        MultipleLabelErrors,
    ) as exception:
        raise HTTPException(
            detail={
                "error": str(exception),
                "label": getattr(exception, "label", None),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return ScoreResponse(
        label=label, score=clothing_score, materials=materials, country=country
    )
