import time
from typing import Union, Self

import httpx

from pinexq_client.job_management.tool import Job
from pinexq_client.job_management.hcos import JobQueryResultHco
from pinexq_client.job_management.model import JobStates


class JobGroup:
    """
    A wrapper class for a group of jobs for easier execution and waiting

    Attributes:
        _client:
            The http client
        _jobs:
            List of jobs in the group
    """

    _client: httpx.Client

    def __init__(self, client: httpx.Client):
        self._jobs: list[Job] = []
        self._client = client

    @classmethod
    def from_query_result(cls, client: httpx.Client, job_query_result: JobQueryResultHco) -> Self:
        """
        Initializes a `JobGroup` object from a JobQueryResultHco object
        Args:
            client: The http client
            job_query_result: The JobQueryResultHco object whose jobs are to be added to the JobGroup

        Returns:
            The newly created `JobGroup` instance
        """
        instance = cls(client)
        for job in job_query_result.iter_flat():
            instance.add_jobs(Job.from_hco(job))
        return instance

    def add_jobs(self, jobs: Union[Job, list[Job]]) -> Self:
        """
        Add a job or multiple jobs to the group

        Args:
            jobs: A job or a list of job objects to be added to the JobGroup

        Returns:
            This `JobGroup` object
        """

        if isinstance(jobs, list):
            self._jobs.extend(jobs)
        else:
            self._jobs.append(jobs)
        return self

    def start_all(self) -> Self:
        """
        Start all jobs

        Returns:
            This `JobGroup` object
        """
        for job in self._jobs:
            job.start()
        return self

    def wait_all(self, *, job_timeout_ms: int = 5000, total_timeout_ms: int | None = None) -> Self:
        """
        Wait for all jobs to complete or error state.
        If the overall timeout elapses and some jobs are not complete, then exception.

        Args:
            job_timeout_ms:
                Individual job timeout in milliseconds. Default is 5000 ms.
            total_timeout_ms:
                Timeout for the whole operation in milliseconds. Default is no timeout.
        Returns:
            This `JobGroup` object
        """
        start_time = time.time()
        for job in self._jobs:
            if total_timeout_ms is not None:
                elapsed_time_ms = (time.time() - start_time) * 1000
                if total_timeout_ms - elapsed_time_ms <= 0:
                    raise Exception("Total timeout exceeded while waiting for jobs.")

            try:
                job.wait_for_state(JobStates.completed, timeout_ms=job_timeout_ms)
            except Exception:
                pass
        return self

    def all_jobs_completed_ok(self) -> bool:
        for job in self._jobs:
            state = job.get_state()
            if state is not JobStates.completed:
                return False
        return True

    def incomplete_jobs(self) -> list[Job]:
        """
        Returns the incomplete jobs

        Returns:
            Count of incomplete jobs
        """
        incomplete_jobs = []
        for job in self._jobs:
            state = job.get_state()
            if state in (JobStates.processing, JobStates.pending):
                incomplete_jobs.append(job)
        return incomplete_jobs

    def jobs_with_error(self) -> list[Job]:
        """
        Returns the list of jobs that produced errors

        Returns:
            List of jobs that produced errors
        """
        return [job for job in self._jobs if job.get_state() == JobStates.error]

    def remove(self, jobs: Job | list[Job]) -> Self:
        """
        Removes given job(s) from the group

        Args:
            jobs:
                The Job instance(s) to be removed
        Returns:
            This `JobGroup` object
        """

        def remove_by_url(job_url: str):
            for existing_job in self._jobs:
                if existing_job.self_link().get_url() == job_url:
                    self._jobs.remove(existing_job)
                    break

        if isinstance(jobs, list):
            for job in jobs:
                remove_by_url(str(job.self_link().get_url()))
        else:
            remove_by_url(str(jobs.self_link().get_url()))

        return self

    def clear(self) -> Self:
        """
        Removes all jobs from the group

        Returns:
            This `JobGroup` object
        """
        self._jobs = []
        return self

    def get_jobs(self) -> list[Job]:
        """
        Returns the list of jobs in the group

        Returns:
            List of jobs in the group
        """
        return self._jobs
