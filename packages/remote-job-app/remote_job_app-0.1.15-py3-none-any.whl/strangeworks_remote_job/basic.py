"""Basic job service."""

import logging
from typing import Any, Tuple

from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Job
from strangeworks_core.types.job import Status as JobStatus
from strangeworks_core.utils import is_empty_str
from sw_product_lib import service
from sw_product_lib.service import RequestContext

from strangeworks_remote_job.artifact import ArtifactGenerator
from strangeworks_remote_job.remote import RemoteJobAPI

from .ex import (
    BillingTransactionError,
    FetchRemoteResultError,
    UpdateJobError,
    UploadJobResultError,
)


def submit(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    payload: dict[str, Any],
    *,
    file_url: list[str] | None = None,
    artifact_generator: ArtifactGenerator | None = None,
    **kwargs,
):
    """Submit a job.

    Parameters
    ----------
    ctx: RequestContext
        Used for making requests to the platform through product lib.
    remote_api: RemoteJobAPI
        Used for making job related requests to remote resources.
    payload: Dict[str, Any]
        Input data for the job.
    file_url: list[str] | None
        List of file URL's which are inputs to remot job request.

    Returns
    -------
    Job:
        Object that contains information about the job entry in platform.
    """
    # If a job slug was passed in, use that to retrieve job entry. Otherwise
    # create a new job entry on the platform.
    # Even if the job submission fails, there should be a record of it on the platform.
    sw_job = service.create_job(ctx)
    logging.info(f"starting remote job submission (slug: {sw_job.slug})")
    estimate = remote_api.estimate_cost(request=payload)
    if estimate > 0.0:
        logging.info(
            f"requesting job clearance for job {sw_job.slug} for the amount {estimate}"  # noqa
        )

        if not service.request_job_clearance(ctx, estimate):
            # did not get clearance. update job status to failed and raise error.
            service.update_job(
                ctx=ctx,
                job_slug=sw_job.slug,
                status=JobStatus.FAILED,
            )
            raise StrangeworksError(
                message=f"Job clearance denied for this resource {ctx.resource_slug}."
            )

    try:
        logging.info(f"submitting remote job request (job slug: {sw_job.slug})")
        if file_url:
            files = [service.get_job_file(ctx=ctx, file_path=f) for f in file_url]
            payload["files"] = files
        job_id = remote_api.submit(
            payload,
            job_slug=sw_job.slug,
            **kwargs,
        )
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            external_identifier=job_id,
        )
        logging.info(
            f"job request submitted (job slug: {sw_job.slug}, remote id:{job_id})"
        )

        if artifact_generator:
            for artifact in artifact_generator(
                remote_id=job_id, input=payload, job_slug=sw_job.slug
            ):
                file = service.upload_job_artifact(
                    artifact.data,
                    ctx=ctx,
                    job_slug=sw_job.slug,
                    file_name=artifact.name,
                    json_schema=artifact.schema,
                    label=artifact.label,
                    sort_weight=artifact.sort_weight,
                    is_hidden=artifact.is_hidden,
                )

                artifact.post_hook(url=file.url, file_slug=file.slug)

    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            status=JobStatus.FAILED,
        )
        raise StrangeworksError(
            message=f"Error occured submitting job remotely (slug: {sw_job.slug}, message: {str(err)})"  # noqa
        ) from err

    return fetch_status(ctx, remote_api, sw_job.slug)


def fetch_status(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
):
    """Fetch job status."""
    try:
        sw_job = service.get_job(ctx, job_slug)
        remote_id: str = sw_job.external_identifier
        current_status: JobStatus = sw_job.status
    except Exception as err:
        raise StrangeworksError(
            f"unable to retrieve job object (slug: {job_slug}, message: {str(err)})"
        ) from err
    # if a job is in COMPLETED status, we log it leave it alone.
    if current_status.is_terminal_state:
        logging.info(
            f"job {job_slug} is in a terminal state {sw_job.status}. It will not be further updated."  # noqa
        )
        return sw_job

    try:
        logging.info(
            f"fetching remote job status for job {job_slug} with remote id {remote_id})"
        )
        remote_status = remote_api.fetch_status(remote_id)
        try:
            sw_status = remote_api.to_sw_status(remote_status)
            logging.info(
                f"fetched status for job {job_slug}: (status: {sw_status}, remote status: {remote_status})"  # noqa
            )
            # if the status of the remote job comes back as COMPLETED, call
            # _handle_job_completion to make sure results are retrieved and
            # cost transactions (if any) are entered on the platform before
            # updating job status to COMPLETED.
            # if something goes wrong, set job status to FAILED and set remote status.
            if sw_status == "COMPLETED":
                try:
                    completed_job = _handle_job_completion(
                        ctx=ctx,
                        remote_api=remote_api,
                        job_slug=job_slug,
                        remote_id=remote_id,
                        remote_status=remote_status,
                    )
                    return completed_job
                except Exception as err:
                    # A failure happened while trying to handle job completion.
                    # Set status to failed, and raise error
                    service.update_job(
                        ctx=ctx,
                        job_slug=job_slug,
                        status=JobStatus.FAILED,
                        remote_status=remote_status,
                    )
                    raise StrangeworksError(
                        message=f"Unable to handle job completion for job {job_slug}, message: {str(err)}"  # noqa
                    ) from err
            # update status and return
            return service.update_job(
                ctx,
                job_slug=job_slug,
                status=remote_api.to_sw_status(remote_status),
                remote_status=remote_status,
            )
        except StrangeworksError as err:
            logging.error(
                f"error updating status for job (slug: {job_slug},  remote id: {remote_id}, message: {str(err)})"  # noqa
            )
            raise err

    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=job_slug,
            status=JobStatus.FAILED,
        )
        raise StrangeworksError(
            message=f"Error updating job status for job {job_slug}, message: {str(err)}"  # noqa
        ) from err


def _handle_fetch_result(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
    remote_id: str,
    remote_status: str | None = None,
    overwrite: bool = False,
    artifact_generator: ArtifactGenerator | None = None,
):
    """Fetch results from remote system.

    Assumes that the remote job has completed and resutls are available. Results are
    retrieved from remote_api as a single object. That single object is then uploaded
    to the platform as an artifact of the given job slug. Upon successful result upload
    to the platform, the finalize method on remote_api will be called to run any
    specific tasks that need to be executed post job completion (freeing resources,
    other cleanup, etc)

    If job cleanup fails, the error will not be propagated back to the caller and will
    be logged instead.
    """
    logging.info(f"fetching job result for job {job_slug}, remote id {remote_id}")

    remote_result = None
    try:
        remote_result = remote_api.fetch_result(remote_id)
        # retrieved remote result, upload it as a job artifact to the platform.
        try:
            logging.info(f"uploading result as artifact for job {job_slug}")
            service.upload_job_artifact(
                remote_result,
                ctx=ctx,
                job_slug=job_slug,
                file_name="result.json",
                overwrite=overwrite,
            )
            logging.info(f"uploaded result for job {job_slug}")
            # call remote cleanup...
            try:
                logging.info(
                    f"Calling cleanup_at_exit for job {job_slug} (remote id {remote_id}"
                )
                remote_api.finalize(remote_id=remote_id, remote_status=remote_status)
            except Exception as err:
                # log this for now since there is nothing that the caller can do.
                logging.error(f"Error from cleanup_at_exit for job {job_slug}")
                logging.exception(err)

            if artifact_generator:
                logging.info(f"generating artifacts for job {job_slug}")
                for artifact in artifact_generator(
                    remote_id=remote_id, input=remote_result, job_slug=job_slug
                ):
                    file = service.upload_job_artifact(
                        artifact.data,
                        ctx=ctx,
                        job_slug=job_slug,
                        file_name=artifact.name,
                        json_schema=artifact.schema,
                        label=artifact.label,
                        sort_weight=artifact.sort_weight,
                        is_hidden=artifact.is_hidden,
                    )
                    artifact.post_hook(url=file.url, file_slug=file.slug)

        except Exception as err:
            raise UploadJobResultError(job_slug=job_slug, remote_id=remote_id) from err

    except Exception as err:
        raise FetchRemoteResultError(job_slug=job_slug, remote_id=remote_id) from err


def _handle_job_completion(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
    remote_id: str,
    remote_status: str | None = None,
):
    """Execute tasks for a successful job completion.

    - Upload job results
    - Update job status to COMPLETED
    - Enter a billing transaction (default: 0)
    """
    logging.info(f"handling job completion for {job_slug}")
    _handle_fetch_result(ctx, remote_api, job_slug, remote_id)

    logging.info(f"setting job status to COMPLETED for job {job_slug}")
    try:
        updated_job = (
            service.update_job(
                ctx,
                job_slug=job_slug,
                status=JobStatus.COMPLETED,
                remote_status=remote_status,
            )
            if remote_status
            else service.update_job(ctx, job_slug=job_slug, status=JobStatus.COMPLETED)
        )

        cost = remote_api.calculate_cost(remote_id=remote_id)
        logging.info(f"computed cost for job {job_slug} is {cost}")
        try:
            description = f"cost for job (slug: {job_slug}, remote_id: {remote_id})"
            if len(description) > 70:
                description = description[:65] + "..."
            service.create_billing_transaction(
                ctx=ctx,
                job_slug=job_slug,
                amount=cost,
                description=description,  # noqa
            )
            logging.info(
                f"created billing transaction for the amount of {cost} USD for job {job_slug}"  # noqa
            )
        except Exception as err:
            raise BillingTransactionError(
                job_slug=job_slug,
                remote_id=remote_id,
                cost=cost,
            ) from err
        finally:
            return updated_job

    except Exception as err:
        raise UpdateJobError(
            job_slug=job_slug, remote_id=remote_id, status=JobStatus.COMPLETED
        ) from err


def fetch_result(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
    overwrite_results: bool = False,
    artifact_generator: ArtifactGenerator | None = None,
):
    """Fetch job result."""
    remote_id, current_status, remote_status = _get_remote_id_and_status(ctx, job_slug)
    if current_status != JobStatus.COMPLETED and not current_status.is_terminal_state:
        # if job is not in COMPLETED status, let fetch_status take over.
        logging.info(
            f"job (slug {job_slug}) is not in COMPLETED state. Fetching remote status."  # noqa
        )
        return fetch_status(ctx, remote_api, job_slug)

    if current_status == JobStatus.COMPLETED and overwrite_results:
        logging.info(
            f"overwriting remote job result for job {job_slug} (remote id {remote_id})"
        )
        _handle_fetch_result(
            ctx,
            remote_api,
            job_slug,
            remote_id,
            remote_status,
            overwrite=overwrite_results,
            artifact_generator=artifact_generator,
        )
        return service.get_job(ctx, job_slug=job_slug)

    if current_status == JobStatus.COMPLETED:
        raise StrangeworksError(
            f"job {job_slug} is in COMPLETED status. Call with overwrite_results=True to force uploading results."  # noqa
        )
    if overwrite_results:
        raise StrangeworksError(
            f"unable to overwrite results for job {job_slug} as it is in {current_status} status"  # noqa
        )

    raise StrangeworksError(
        f"unable to fetch results for job {job_slug} as it is in {current_status} status."  # noqa
    )


def cancel(ctx: RequestContext, remote_api: RemoteJobAPI, job_slug: str):
    """Cancel a job.

    Parameters
    ----------
    ctx: RequestContext
        Used for making requests to the platform through product lib.
    remote_api: RemoteJobAPI
        Used for making job related requests to remote resources.
    job_slug: str
        Job identifier.
    """
    sw_job: Job = service.get_job(ctx=ctx, job_slug=job_slug)

    if sw_job.status.is_terminal_state():
        # log and return
        logging.info(f"job ({job_slug}) is already in a terminal state {sw_job.status}")
        return sw_job

    try:
        remote_api.cancel(sw_job.external_identifier)
    except Exception as err:
        raise StrangeworksError(
            message=f"error while cancelling job {job_slug}"
        ) from err

    return service.update_job(
        ctx=ctx,
        job_slug=job_slug,
        status=JobStatus.CANCELLED,
    )


def _get_remote_id_and_status(
    ctx: RequestContext, job_slug: str
) -> Tuple[str, JobStatus, str]:
    sw_job: Job = service.get_job(ctx, job_slug)
    if is_empty_str(sw_job.external_identifier):
        raise StrangeworksError(
            f"no external identifier found for job (slug: {job_slug})"
        )
    return (sw_job.external_identifier, sw_job.status, sw_job.remote_status)
