import json
import logging
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status

from src.app.crud.score import compute_score
from src.app.schemas.score import LabelMessage, ScoreResponse
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


class RouteType:
    post_compute_score = "/post_compute_score"


def handle_error(exception: Exception, label: Optional[str] = None):
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
        labels = []
        if score_message.images_labels is not None:
            labels += score_message.images_labels
        elif score_message.images_urls is not None:
            labels += [ocr(image_url=x) for x in score_message.images_urls]
        elif score_message.images is not None:
            labels += [ocr(image_bytes=x) for x in score_message.images]
        else:
            raise Exception(
                f"At least one of "
                f"{LabelMessage.images_labels} {LabelMessage.images_urls} "
                f"{LabelMessage.images} fields must be provided"
            )
        label = " ".join(labels)
        clothing_score, materials, country = compute_score(
            label=label,
            interpreter=interpreter,
            environment_ranking=score_message.preferences.index(Criteria.environment)
            + 1,
            societal_ranking=score_message.preferences.index(Criteria.societal) + 1,
            animal_ranking=score_message.preferences.index(Criteria.animal) + 1,
            health_ranking=score_message.preferences.index(Criteria.health) + 1,
            return_found_elements=True,
        )
        return ScoreResponse(
            label=label, score=clothing_score, materials=materials, country=country
        )
    except Exception as e:
        handle_error(exception=e, label=label)
