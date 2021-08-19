import logging

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.helper.google_interface import GoogleInterface
from src.app.routes import score

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

security = HTTPBearer()


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
    app = FastAPI()

    api_router = APIRouter()
    api_router.include_router(
        score.router,
        prefix="/score",
        tags=["score"],
        # dependencies=[Depends(check_security)],
    )
    app.include_router(api_router, prefix="/v1")
    return app


app = get_application()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Wrong body: {exc.body} pydantic error: {str(exc)}")
    return PlainTextResponse(str(exc), status_code=400)


origins = [
    "http://localhost",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
