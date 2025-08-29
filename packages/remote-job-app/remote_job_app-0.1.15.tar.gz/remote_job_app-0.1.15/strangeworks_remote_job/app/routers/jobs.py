"""Job API v2.0.0."""

import importlib
from typing import Optional

from fastapi import APIRouter, Request
from strangeworks_core.config.config import Config
from strangeworks_core.errors.error import StrangeworksError

from .types.job import JobRequest, JobResponse, SubmitRequest


router = APIRouter(prefix="/jobs", tags=["jobs"])

_cfg = Config()

batch_flag = (
    bool(_cfg.get("submission", "async_modal"))
    if _cfg.get("submission", "async_modal")
    else False
)
# Define a function to dynamically import a module
module_name = (
    "strangeworks_remote_job.modal" if batch_flag else "strangeworks_remote_job.basic"
)

try:
    module = importlib.import_module(module_name)
except ImportError as e:
    raise StrangeworksError(message=f"Error importing module {module_name}: {e}")


@router.post("/submit")
async def run_job(request: Request, submit_request: Optional[SubmitRequest] = None):
    """Submit a job run request."""
    ctx = request.state.params.ctx
    data = submit_request.input if submit_request else None
    file_url = submit_request.file_url if submit_request else None
    remote_api = request.state.params.remote_api
    artifact_generator = request.state.params.artifact_generator
    job = module.submit(ctx, remote_api, data, file_url, artifact_generator)
    return JobResponse(job)


@router.post("/fetch-status")
async def list_job_details(job_request: JobRequest, request: Request):
    """Fetch job status."""
    ctx = request.state.params.ctx
    remote_api = request.state.params.remote_api
    job = module.fetch_status(ctx, remote_api, job_request.slug)
    return JobResponse(job)


@router.post("/fetch-result")
def get_job_results(job_request: JobRequest, request: Request):
    """Fetch Job Results."""
    ctx = request.state.params.ctx
    remote_api = request.state.params.remote_api
    artifact_generator = request.state.params.artifact_generator
    job = module.fetch_result(
        ctx,
        remote_api,
        job_request.slug,
        overwrite_results=False,
        artifact_generator=artifact_generator,
    )
    return JobResponse(job)


@router.post("/cancel")
def cancel_job(job_request: JobRequest, request: Request):
    """Send a request to cancel a job."""
    ctx = request.state.params.ctx
    remote_api = request.state.params.remote_api
    job = module.cancel(ctx, remote_api, job_request.slug)
    return JobResponse(job)
