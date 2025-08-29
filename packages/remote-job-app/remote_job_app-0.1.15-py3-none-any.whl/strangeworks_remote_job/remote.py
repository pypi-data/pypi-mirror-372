"""Remote job type."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class RemoteJobAPI(ABC):
    """Remote job API."""

    @classmethod
    @abstractmethod
    def submit(
        self,
        payload: Dict[str, Any],
        *,
        job_slug: str | None = None,
        **kwargs,
    ) -> str:
        """Submit a Job.

        Parameters
        ----------
        payload: dict
            contents of the request (circuits, models, etc)
        job_slug: str | None
            strangeworks job slug
        **kwargs:
        """
        pass

    @abstractmethod
    def fetch_status(self, remote_id: str) -> str:
        """Fetch Job Status.

        Parameters
        ----------
        remote_id: str
            identifier used to perform actions on job on remote system.
        """
        pass

    @abstractmethod
    def fetch_result(self, remote_id: str) -> str:
        """Get Job Result.

        Parameters
        ----------
        remote_id: str
            identifier used to perform actions on job on remote system.
        """
        pass

    def cancel(self, remote_id: str) -> str:
        """Cancel Job.

        Parameters
        ----------
        remote_id: str
            identifier used to perform actions on job on remote system.
        """
        raise NotImplementedError("cancel not implemented")

    @abstractmethod
    def to_sw_status(self, remote_status: str) -> str:
        """Convert remote status to Strangeworks status."""
        pass

    def estimate_cost(self, **kwargs) -> float:
        """Estimate Job Cost.

        If there is a way to estimate the cost of a job, the derived class
        must implement this function. If its not possible to estimate the cost
        but the job will have a billing transaction associated with it, the
        derived class should return a value that should be the minimum about necessary
        to run a job.

        If the estimated cost is a negative number, it is assumed that there is no
        cost associated with the job.
        """
        return -1.0

    def calculate_cost(self, remote_id: str) -> float:
        """Calculate job cost.

        If submitting a remote job is not free, the derived class must
        implement this function to calculate the cost of the job.

        Parameters
        ----------
        remote_id: str
            identifier used to perform actions on job on remote system.

        Return
        ------
        : float
            Amount to be charged as USD.
        """
        return 0.0

    def finalize(self, remote_id: str, remote_status: str | None = None, **kwargs):
        """Cleanup actions after job has reached terminal state.

        This method should be implemented if there are actions that need
        to be taken to free up resources, etc once a job has
        completed.

        Parameters
        ----------
        remote_id: str
            identifier used to perform actions on job on remote system.
        remote_status: str
            last known status from the remote system.
        """
        return
