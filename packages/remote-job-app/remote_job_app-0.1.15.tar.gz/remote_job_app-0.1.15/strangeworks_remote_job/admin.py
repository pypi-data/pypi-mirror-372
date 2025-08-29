"""admin.py."""

import importlib
import logging

from strangeworks_core.config.config import Config
from strangeworks_core.errors.error import StrangeworksError
from sw_product_lib import service
from sw_product_lib.service import RequestContext
from sw_product_lib.types.job import Job, JobStatus


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


logger = logging.getLogger()


def update_job_status(ctx: RequestContext, remote_api):
    """Update job statuses."""
    logger.info("start job update for {ctx.product_slug}")
    jobs: dict[JobStatus, Job] = service.get_jobs_by_statuses(
        ctx=ctx, statuses=[JobStatus.CREATED, JobStatus.QUEUED, JobStatus.RUNNING]
    )

    for job_status, job_list in jobs.items():
        logger.info(f"starting job updates for jobs with status {job_status}")
        for job in job_list:
            # TODO: fix upload_job_artifact so that it doesn't require a resource slug
            # and then remove this ugly hack.
            ctx.resource_slug = job.resource.slug
            try:
                logger.info(
                    f"fetching status for job {job.slug}, current status: {job.status}"
                )
                updated_job = module.fetch_status(ctx, remote_api, job.slug)
                logger.info(
                    f"updated job {updated_job.slug} status prior: {job.status}, updated: {updated_job.status}"  # noqa
                )
            except BaseException as ex:
                logging.error(f"error updating status for job {job.slug}")
                logging.exception(ex)
