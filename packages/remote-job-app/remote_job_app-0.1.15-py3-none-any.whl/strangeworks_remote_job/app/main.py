"""main.py."""

import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from strangeworks_core.config.config import Config
from strangeworks_core.errors.error import StrangeworksError

from strangeworks_remote_job.app.middleware import RequestContextMiddleware
from strangeworks_remote_job.app.routers import admin, jobs


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strangeworks_remote_job")
gql_logger = logging.getLogger("gql.transport.requests")
gql_logger.setLevel(logging.DEBUG)

cfg = Config()

logger.info(f"config sources: {cfg._cfg_sources}")

app_config = {
    k: v
    for k, v in {
        "title": cfg.get("title", "app"),
        "summary": cfg.get("summary", "app"),
        "description": cfg.get("description", "app"),
        "version": cfg.get("version", "app"),
        "contact": cfg.get("contact", "app"),
        "root_path": cfg.get("root_path", "app"),
    }.items()
    if v
}

app = FastAPI(
    title=app_config.get("title", "Strangeworks Remote App"),
    summary=app_config.get("summary", None),
    version=app_config.get("version", "0.1.0"),
    description=app_config.get("description", "Strangeworks Remote App"),
    contact=app_config.get(
        "contact",
        {
            "name": "Strangeworks",
            "email": "hello@strangeworks.com",
        },
    ),
    root_path=app_config.get("root_path", os.getenv("ROOT_PATH", "")),
)


@app.exception_handler(StrangeworksError)
async def http_exception_handler(
    request: Request, exc: StrangeworksError
) -> JSONResponse:
    """Exception handler for StrangeworksError exceptions.

    More info on how this works here: https://tinyurl.com/2hfr9fwj

    Parameters
    ----------
    requst: Request
        request object.
    exc: StrangeworksError
        StrangeworksError exception.

    Return
    ------
    :JSONResponse
        The exception represented as a JSONResponse object.
    """
    logging.exception(exc)
    return JSONResponse(status_code=400, content={"error": exc.message})


# add routers
app.add_middleware(RequestContextMiddleware)

app.include_router(jobs.router)
app.include_router(admin.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check."""
    return {"status": "ok"}
