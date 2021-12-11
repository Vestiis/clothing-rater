import logging

from fastapi import APIRouter, Body, Depends, HTTPException

from src.app.crud.score import compute_score
from src.app.schemas.score import LabelMessage, ScoreResponse
from src.exceptions import (
    CountryNotFound,
    MaterialNotFound,
    MissingMaterialPercentage,
    TextNotFound,
)
from src.interpreter import Interpreter, get_interpreter
from src.ocr import Ocr, get_ocr
from src.scorer import Criteria

router = APIRouter()

logger = logging.getLogger(__name__)


class RouteType:
    post_compute_score = "/post_compute_score"


def handle_error(exception: Exception):
    if (
        isinstance(exception, MaterialNotFound)
        or isinstance(exception, CountryNotFound)
        or isinstance(exception, TextNotFound)
        or isinstance(exception, MissingMaterialPercentage)
    ):
        raise HTTPException(detail=str(exception), status_code=422)
    else:
        raise HTTPException(detail=str(exception), status_code=500)


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
    try:
        if score_message.images_labels is not None:
            labels = score_message.images_labels
        elif score_message.images_urls is not None:
            labels = [ocr(image_url=x) for x in score_message.images_urls]
        elif score_message.images is not None:
            labels = [ocr(image_bytes=x) for x in score_message.images]
        else:
            raise Exception(
                f"At least one of "
                f"{LabelMessage.images_labels} {LabelMessage.images_urls} "
                f"{LabelMessage.images} fields must be provided"
            )
        clothing_score, materials, country = compute_score(
            label=" ".join(labels),
            interpreter=interpreter,
            environment_ranking=score_message.preferences.index(Criteria.environment)
            + 1,
            societal_ranking=score_message.preferences.index(Criteria.societal) + 1,
            animal_ranking=score_message.preferences.index(Criteria.animal) + 1,
            health_ranking=score_message.preferences.index(Criteria.health) + 1,
            return_found_elements=True,
        )
        return ScoreResponse(score=clothing_score, materials=materials, country=country)
    except Exception as e:
        handle_error(e)
