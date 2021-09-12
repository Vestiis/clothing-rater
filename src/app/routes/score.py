import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.crud.score import compute_score
from src.app.schemas.score import LabelMessage, ScoreResponse
from src.db.database import get_db
from src.ocr import Ocr, get_ocr
from src.words_matcher import WordsMatcher, get_words_matcher

router = APIRouter()

logger = logging.getLogger(__name__)


class RouteType:
    post_compute_score_from_image_bytes = "/post_compute_score_from_image_bytes"
    post_compute_score_from_image_url = "/post_compute_score_from_image_url"
    post_compute_score_from_image_label = "/post_compute_score_from_image_label"


@router.post(
    RouteType.post_compute_score_from_image_bytes, response_model=ScoreResponse
)
def post_compute_score_from_image_bytes(
    *,
    score_message: LabelMessage = Body(..., embed=False),
    ocr: Ocr = Depends(get_ocr),
    words_matcher: WordsMatcher = Depends(get_words_matcher),
    db: Session = Depends(get_db),
    # credentials: HTTPAuthorizationCredentials = Security(security) # would this work to have the uuid that would allow me to retrieve
    # info about the user?
):
    try:
        clothing_score = compute_score(
            label=" ".join(ocr(image_bytes=x) for x in score_message.images),
            words_matcher=words_matcher,
            db=db,
            ecology_importance=1,
            societal_importance=1,
        )
        return ScoreResponse(score=clothing_score)
    except Exception as e:
        logger.error(e)
        raise HTTPException(detail=str(e), status_code=500)


@router.post(RouteType.post_compute_score_from_image_url, response_model=ScoreResponse)
def post_compute_score_from_image_url(
    *,
    score_message: LabelMessage = Body(..., embed=False),
    ocr: Ocr = Depends(get_ocr),
    words_matcher: WordsMatcher = Depends(get_words_matcher),
    db: Session = Depends(get_db),
):
    try:
        clothing_score = compute_score(
            label=" ".join(ocr(image_url=x) for x in score_message.images_urls),
            words_matcher=words_matcher,
            db=db,
            ecology_importance=1,
            societal_importance=1,
        )
        return ScoreResponse(score=clothing_score)
    except Exception as e:
        logger.error(e)
        raise HTTPException(detail=str(e), status_code=500)


@router.post(
    RouteType.post_compute_score_from_image_label, response_model=ScoreResponse
)
def post_compute_score_from_image_label(
    *,
    score_message: LabelMessage = Body(..., embed=False),
    words_matcher: WordsMatcher = Depends(get_words_matcher),
    db: Session = Depends(get_db),
):
    try:
        clothing_score = compute_score(
            label=" ".join(x for x in score_message.images_labels),
            words_matcher=words_matcher,
            db=db,
            ecology_importance=1,
            societal_importance=1,
        )
        return ScoreResponse(score=clothing_score)
    except Exception as e:
        logger.error(e)
        raise HTTPException(detail=str(e), status_code=500)
