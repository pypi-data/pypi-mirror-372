"""Remote Job App."""
from sw_product_lib.service import RequestContext
from sw_product_lib.types.job import Job

from . import basic
from .remote import RemoteJobAPI


class RemoteJobApp:
    """Create a Basic Strangeworks Application From a RemoteJobAPI implementation."""

    def __init__(self, ctx: RequestContext, remote_api: RemoteJobAPI):
        """Initialize App."""
        self.remote_api: RemoteJobAPI = remote_api
        self.ctx: RequestContext = ctx

    def submit(self, payload: dict, **kwargs) -> Job:
        """Submit a Job."""
        return basic.submit(self.ctx, self.remote_api, payload)

    def fetch_status(self, job_slug: str, **kwargs) -> Job:
        """Fetch Remote Job Status."""
        ...

    def fetch_result(self, job_slug: str) -> Job:
        """Fetch Remote Job Result.

        Used to retrieve results of the request identified at a remote system with the
        external_identifier field for the job corresponding to the given job slug.

        Should not be called directly. Let fetch_status call this as necessary.
        """
        ...
