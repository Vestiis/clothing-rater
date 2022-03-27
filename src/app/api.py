import logging

from fastapi import APIRouter, FastAPI, HTTPException, Security
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.helper.google_interface import GoogleInterface
from src.app.routes import score
from src.app.schemas.score import LabelMessageNoImageSourceError

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

security = HTTPBearer()

APP_PREFIX = "/v1"


def check_security(credentials: HTTPAuthorizationCredentials = Security(security)):
    authorization = credentials.credentials
    if authorization is None or not GoogleInterface().verify_id_token(
        id_token_to_verify=authorization
    ):
        logger.error(f"No Authorization ! {authorization}")
        raise HTTPException(
            detail="Forbidden: Wrong token for authentification", status_code=403
        )


def get_application() -> FastAPI:
    app = FastAPI(debug=True)

    api_router = APIRouter(prefix=APP_PREFIX)
    api_router.include_router(score.router,)  # dependencies=[Depends(check_security)],
    app.include_router(api_router)  # , dependencies=[Depends(check_security)

    @app.exception_handler(LabelMessageNoImageSourceError)
    async def label_message_no_image_source_exception_handler(request, exc):
        logger.error(f"Pydantic error: {str(exc)}")
        return PlainTextResponse(str(exc), status_code=400)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error(f"Wrong body: {exc.body} pydantic error: {str(exc)}")
        return PlainTextResponse(str(exc), status_code=400)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://localhost:8081"],
        allow_origin_regex="https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = get_application()
