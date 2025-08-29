"""ex.py."""
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Status as JobStatus


class RemoteJobError(StrangeworksError):
    """RemoteJobError."""

    def __init__(
        self,
        job_slug: str | None = None,
        remote_id: str | None = None,
        **kwargs,
    ):
        """Initialize object."""
        super().__init__(**kwargs)
        self.remote_id = remote_id
        self.job_slug = job_slug


class UpdateJobError(RemoteJobError):
    """UpdateJobError."""

    def __init__(self, status: JobStatus, **kwargs):
        """Initialize object."""
        super().__init__(**kwargs)
        self.message = (
            "Error occurred while updating status for job {self.job_slug} to {status}"
        )


class FetchRemoteResultError(RemoteJobError):
    """FetchRemoteResultError."""

    def __init__(self, **kwargs):
        """Initialize object."""
        super().__init__(**kwargs)


class UploadJobResultError(RemoteJobError):
    """UploadJobResultError."""

    def __init__(self, **kwargs):
        """Initialize object."""
        super().__init__(**kwargs)


class BillingTransactionError(RemoteJobError):
    """BillingTransactionError."""

    def __init__(self, cost: float, **kwargs):
        """Initialize object."""
        super().__init__(**kwargs)
        self.message = f"Error occurred while creating a billing transaction for the amount of {cost}USD for job {self.job_slug}"  # noqa
