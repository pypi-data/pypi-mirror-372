"""admin.py."""

import logging

from fastapi import APIRouter, Request
from sw_product_lib.service import RequestContext

from strangeworks_remote_job import admin


router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger()


@router.get("/update-jobs")
async def update_jobs(request: Request):
    """Do Job Updates."""
    ctx: RequestContext = request.state.params.ctx
    remote_api = request.state.params.remote_api
    return admin.update_job_status(ctx, remote_api)
