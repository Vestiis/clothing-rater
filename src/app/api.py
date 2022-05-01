import json
import logging
from typing import Any

import starlette.requests
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.app.helper.google_interface import GoogleInterface
from src.app.routes import score

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

security = HTTPBearer()

APP_VERSION = "/v1"


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

    api_router = APIRouter(prefix=APP_VERSION)
    api_router.include_router(score.router)  # dependencies=[Depends(check_security)],

    app.include_router(api_router)  # , dependencies=[Depends(check_security)

    async def request_json_store_body(self) -> Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        self.scope["body"] = self._json
        return self._json

    # override starlette json function to store the body in the request scope
    # when it is called
    starlette.requests.Request.json = request_json_store_body

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request, exc):
        logger.error(
            f"{exc} error for request method: {request.method} "
            f"url: {request.url} and body: {request.scope.get('body')}"
        )
        return await http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def handle_exception(request, exc):
        logger.error(
            f"{exc} error for request method: {request.method} "
            f"url: {request.url} and body: {request.scope.get('body')}"
        )
        raise exc

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request, exc):
        logger.error(
            f"{exc} error for request method: {request.method} "
            f"url: {request.url} and body: {request.scope.get('body')}"
        )
        return await request_validation_exception_handler(request, exc)

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
