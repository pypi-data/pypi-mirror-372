import json as json_
import warnings
from typing import Any, Self, List

import httpx
from httpx import URL
from pydantic import BaseModel, ConfigDict

from pinexq_client.core import Link, MediaTypes, ClientException, ApiException
from pinexq_client.core.polling import wait_until, PollingException
from pinexq_client.job_management.enterjma import enter_jma
from pinexq_client.job_management.hcos import WorkDataLink, ProcessingStepLink, InputDataSlotHco, OutputDataSlotHco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.hcos.job_hco import (
    GenericProcessingConfigureParameters,
    JobHco,
    JobLink,
)
from pinexq_client.job_management.hcos.job_query_result_hco import JobQueryResultHco
from pinexq_client.job_management.hcos.jobsroot_hco import JobsRootHco
from pinexq_client.job_management.hcos.processingsteproot_hco import (
    ProcessingStepsRootHco,
)
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import (
    CreateJobParameters,
    CreateSubJobParameters,
    FunctionNameMatchTypes,
    JobFilterParameter,
    JobQueryParameters,
    JobSortPropertiesSortParameter,
    JobStates,
    ProcessingStepFilterParameter,
    ProcessingStepQueryParameters,
    ProcessingView,
    SelectProcessingParameters,
    SelectWorkDataCollectionForDataSlotParameters,
    SelectWorkDataForDataSlotParameters,
    SetJobTagsParameters, RapidJobSetupParameters, InputDataSlotParameter,
)
from pinexq_client.job_management.tool.processing_step import ProcessingStep
from pinexq_client.job_management.tool.workdata import WorkData


class InputDataSlotParameterFlexible(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )
    index: int
    work_data_urls: List[str] | None = None
    work_data_instances: List[WorkData] | None = None

    @classmethod
    def create(cls, *,
        index: int,
        work_data_urls: List[WorkDataLink] | None = None,
        work_data_instances: List[WorkData] | None = None
    ) -> "InputDataSlotParameterFlexible":
        """Creates an instance of InputDataSlotParameterFlexible that can be used to assign work data to a job.

        Args:
            index: The index of the input data slot.
            work_data_urls: A list of URLs pointing to the work data.
            work_data_instances: A list of WorkData instances.

        Returns:
            An instance of InputDataSlotParameterFlexible.
        """
        if sum(p is not None for p in [work_data_urls, work_data_instances]) != 1:
            raise ValueError("Exactly one parameter must be provided")

        if work_data_instances is not None:
            if not isinstance(work_data_instances, list) or any(
                    not isinstance(i, WorkData) for i in work_data_instances):
                raise Exception('Instance passed to "work_data_instances" is not of type "list[WorkData]"')
            work_data_urls = [work_data_instance.self_link() for work_data_instance in work_data_instances]
        return InputDataSlotParameterFlexible(
            index=index,
            work_data_urls=[str(wd.get_url()) for wd in work_data_urls] if work_data_urls else None,
            work_data_instances=None
        )

class Job:
    """Convenience wrapper for handling JobHcos in the JobManagement-Api.

    This wrapper allows the API to be used with a fluent-style builder pattern:

    job = (
        Job(client)
        .create(name='JobName')
        .select_processing(processing_step='job_processing')
        .configure_parameters(**job_parameters)
        .start()
        .wait_for_state(JobStates.completed)
        .delete()
    )
    """

    _client: httpx.Client
    _entrypoint: EntryPointHco
    _jobs_root: JobsRootHco
    _processing_step_root: ProcessingStepsRootHco
    job_hco: JobHco | None = None  # Internal hco of the wrapper. This is updated by this class. You should not take a reference to this object.

    def __init__(self, client: httpx.Client):
        """

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
        """
        self._client = client
        self._entrypoint = enter_jma(client)
        self._jobs_root = self._entrypoint.job_root_link.navigate()
        self._processing_step_root = (
            self._entrypoint.processing_step_root_link.navigate()
        )

    def create(self, name: str) -> Self:
        """
        Creates a new job by name.

        Args:
            name: Name of the job to be created

        Returns:
            The newly created job as `Job` object
        """
        job_link = self._jobs_root.create_job_action.execute(
            CreateJobParameters(name=name)
        )
        self._get_by_link(job_link)
        return self

    def _get_by_link(self, job_link: JobLink):
        self.job_hco = job_link.navigate()

    @classmethod
    def from_hco(cls, job: JobHco) -> Self:
        """Initializes a `Job` object from an existing JobHco object.

        Args:
            job: The 'JobHco' to initialize this job from.

        Returns:
            The newly created job as `Job` object.
        """
        job_instance = cls(job._client)
        job_instance.job_hco = job
        return job_instance

    @classmethod
    def from_url(cls, client: httpx.Client, job_url: URL) -> Self:
        """Initializes a `Job` object from an existing job given by its link as URL.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            job_url:

        Returns:
            The newly created job as `Job` object
        """
        link = Link.from_url(
            job_url,
            [str(Relations.CREATED_RESSOURCE)],
            "Created sub-job",
            MediaTypes.SIREN,
        )
        job_instance = cls(client)
        job_instance._get_by_link(JobLink.from_link(client, link))
        return job_instance

    def create_sub_job(self, name: str) -> "Job":
        """Create a new job by name as a sub-job of the current one.

        Args:
            name:
                Name of the job to be created
        Returns:
            The newly created job as `Job` object
        """
        self._raise_if_no_hco()
        parent_job_url = self.job_hco.self_link.get_url()
        sub_job_link = self._jobs_root.create_subjob_action.execute(
            CreateSubJobParameters(name=name, parent_job_url=str(parent_job_url))
        )
        sub_job = Job(self._client)
        sub_job._get_by_link(sub_job_link)
        return sub_job

    def refresh(self) -> Self:
        """Updates the job from the server

        Returns:
            This `Job` object, but with updated properties.
        """
        self._raise_if_no_hco()
        self.job_hco = self.job_hco.self_link.navigate()
        return self

    def get_state(self) -> JobStates:
        """Returns the current state of this job from the server

        Returns:
            The current state of this `Job` from JobStates
        """
        self.refresh()
        return self.job_hco.state

    def get_name(self) -> str:
        """Returns the name of this job

        Returns:
            The name of this `Job`
        """
        self.refresh()
        return self.job_hco.name

    def select_processing(
            self,
            function_name: str | None = None,
            function_version: str | None = None,
            *,
            processing_step_link: ProcessingStepLink | None = None,
            processing_step_instance: ProcessingStep | None = None
    ) -> Self:
        """Set the processing step for this job given by name. This will query all
        processing steps of this name from the server and select the first result.

        Args:
            function_name: Name of the processing step as string
            function_version: Version of the processing step as string
            processing_step_link: A ProcessingStepLink instance pointing to the resource
            processing_step_instance: A ProcessingStep (not the Hco) instance

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        if sum(p is not None for p in [function_name, processing_step_link, processing_step_instance]) != 1:
            raise ValueError("Exactly one parameter must be provided")

        if processing_step_link is not None:
            if not isinstance(processing_step_link, ProcessingStepLink):
                raise TypeError('Instance passed to "processing_step_link" is not of type "ProcessingStepLink"')
            processing_url = processing_step_link.get_url()
        elif processing_step_instance is not None:
            if not isinstance(processing_step_instance, ProcessingStep):
                raise TypeError('Instance passed to "processing_step_instance" is not of type "ProcessingStep"')
            processing_url = processing_step_instance.self_link().get_url()
        else:
            if not isinstance(function_name, str):
                raise TypeError('Instance passed to "function_name" is not of type "str"')
            # ToDo: provide more parameters to query a processing step
            query_param = ProcessingStepQueryParameters(
                filter=ProcessingStepFilterParameter(
                    function_name=function_name,
                    function_name_match_type=FunctionNameMatchTypes.match_exact,
                    version=function_version,
                )
            )
            query_result = self._processing_step_root.query_action.execute(query_param)
            if len(query_result.processing_steps) != 1:
                raise NameError(f"No processing step with the name '{function_name}' registered!")
            # Todo: For now we choose the first and only result. Make this more flexible?
            processing_url = query_result.processing_steps[0].self_link.get_url()

        self.job_hco.select_processing_action.execute(
            SelectProcessingParameters(processing_step_url=str(processing_url))
        )

        self.refresh()

        return self

    def configure_parameters(self, **parameters: Any) -> Self:
        """Set the parameters to run the processing step with.

        Args:
            **parameters: Any keyword parameters provided will be forwarded as parameters
                to the processing step function.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.configure_processing_action.execute(
            GenericProcessingConfigureParameters.model_validate(parameters)
        )

        self.refresh()
        return self

    def start(self) -> Self:
        """Start processing this job.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.start_processing_action.execute()
        self.refresh()
        return self

    def get_result(self) -> Any:
        """Get the return value of the processing step after its completion.

        This value is not defined before completion, so check the state first or
        wait explicitly for it to complete.

        Returns:
            The result of the processing step
        """
        # TODO: return Sentinel or Exception on 'NotDoneYet'
        # TODO: handle return value equivalent to asyncio's Future objects
        self.refresh()
        result = self.job_hco.result
        return json_.loads(result) if result else None

    def wait_for_state(self, state: JobStates, timeout_ms: int = 5000, polling_interval_ms: int = 1000) -> Self:
        """Wait for this job to reach a state. If the job enters error state an exception is risen

        Args:
            state: The state to wait for. After the job enters this state this function returns.
            timeout_ms: Time span in milliseconds to wait for reaching the state before raising an exception.
            polling_interval_ms: will determine how fast the API is polled for updates.
            Note that low values will produce unnecessary load.

        Returns:
            This `Job` object


        """
        self._raise_if_no_hco()
        try:
            wait_until(
                condition=lambda: self.get_state() == state,
                timeout_ms=timeout_ms,
                timeout_message="Waiting for job completion",
                error_condition=lambda: self.job_hco.state == JobStates.error,
                polling_interval_ms=polling_interval_ms
            )
        except TimeoutError as timeout:
            raise TimeoutError(
                f"Job did not reach state: '{state.value}' "
                f"current state: '{self.get_state().value}'. Error:{str(timeout)}"
            )
        except PollingException:
            if self.job_hco.state == JobStates.error:
                error_reason = self.job_hco.error_description
                raise PollingException(f"Job failed'. Error:{error_reason}")
            raise PollingException("Job failed")

        return self

    def wait_for_completion(self, timeout_ms: int = 60000, polling_interval_ms: int = 500) -> Self:
        """Wait for this job to reach the state 'completed'.

        Args:
            timeout_ms: Timeout to wait for the job to reach the next state.
            polling_interval_ms: will determine how fast the API is polled for updates.
            Note that low values will produce unnecessary load.

        Returns:
            This `Job` object
        """
        return self.wait_for_state(JobStates.completed, timeout_ms, polling_interval_ms)

    def assign_input_dataslot(
            self,
            index: int,
            *,
            work_data_link: WorkDataLink | None = None,
            work_data_instance: WorkData | None = None
    ) -> Self:
        """Assign WorkData to DataSlots.

        Args:
            index: The numerical index of the dataslot.
            work_data_link:  WorkData given by its URL
            work_data_instance: WorkData instance

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        if sum(p is not None for p in [work_data_link, work_data_instance]) != 1:
            raise ValueError("Exactly one parameter must be provided")

        if work_data_instance is not None:
            if not isinstance(work_data_instance, WorkData):
                raise Exception('Instance passed to "work_data_instance" is not of type "WorkData"')
            work_data = work_data_instance.self_link()
        else:
            if not isinstance(work_data_link, WorkDataLink):
                raise Exception('Instance passed to "work_data_link" is not of type "WorkDataLink"')
            work_data = work_data_link

        dataslot = self.job_hco.input_dataslots[index]
        dataslot.select_workdata_action.execute(
            parameters=SelectWorkDataForDataSlotParameters(
                work_data_url=str(work_data.get_url())
            )
        )
        self.refresh()

        return self

    def assign_collection_input_dataslot(
            self,
            index: int,
            *,
            work_data_links: list[WorkDataLink] | None = None,
            work_data_instances: list[WorkData] | None = None
    ) -> Self:
        """Assign WorkData to DataSlots.

        Args:
            index: The numerical index of the dataslot.
            work_data_links:  WorkData collection given by their URLs
            work_data_instances: Collection of WorkData instances

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        if sum(p is not None for p in [work_data_links, work_data_instances]) != 1:
            raise ValueError("Exactly one parameter must be provided")

        if work_data_instances is not None:
            if not isinstance(work_data_instances, list) or any(
                    not isinstance(i, WorkData) for i in work_data_instances):
                raise Exception('Instance passed to "work_data_instances" is not of type "list[WorkData]"')
            work_datas = [work_data_instance.self_link() for work_data_instance in work_data_instances]
        else:
            if not isinstance(work_data_links, list) or any(not isinstance(i, WorkDataLink) for i in work_data_links):
                raise Exception('Instance passed to "work_data_links" is not of type "list[WorkDataLink]"')
            work_datas = work_data_links

        dataslot = self.job_hco.input_dataslots[index]
        dataslot.select_workdata_collection_action.execute(
            parameters=SelectWorkDataCollectionForDataSlotParameters(
                work_data_urls=[str(workdata_link.get_url()) for workdata_link in work_datas]
            )
        )
        self.refresh()

        return self

    def clear_input_dataslot(self, index: int) -> Self:
        """Clear the selected WorkData for a dataslot.

        Args:
            index: he numerical index of the dataslot.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        dataslot = self.job_hco.input_dataslots[index]

        # already cleared
        if not dataslot.clear_workdata_action:
            return

        dataslot.clear_workdata_action.execute()
        self.refresh()

        return self

    def _get_sub_jobs(
            self,
            sort_by: JobSortPropertiesSortParameter | None = None,
            state: JobStates | None = None,
            name: str | None = None,
            show_deleted: bool | None = None,
            processing_step_url: str | None = None,
    ) -> JobQueryResultHco:
        self._raise_if_no_hco()
        filter_param = JobFilterParameter(
            is_sub_job=True,
            parent_job_url=str(self.job_hco.self_link.get_url()),
            state=state,
            name=name,
            show_deleted=show_deleted,
            processing_step_url=processing_step_url,
        )

        query_param = JobQueryParameters(sort_by=sort_by, filter=filter_param)
        job_query_result = self._jobs_root.job_query_action.execute(query_param)
        return job_query_result

    def get_sub_jobs(self, **tbd):
        # todo: Query result iterator to go through paginated result
        raise NotImplementedError

    def sub_jobs_in_state(self, state: JobStates) -> int:
        """Query how many sub-job are in a specific state.

        Args:
            state: Job state as `JobStates` enum.

        Returns:
            The number of sub-jobs in the requested state.
        """
        query_result = self._get_sub_jobs(state=state)
        return query_result.total_entities

    def wait_for_sub_jobs_complete(self, timeout_ms: int = 60000, polling_interval_ms: int = 1000) -> Self:
        """Wait for all sub-jobs to reach the state 'completed'.

        This function will block execution until the state is reached or raise an exception
        if the operation timed out or a sub-job returned an error. Only started jobs will be watched.

        Args:
            timeout_ms: Timeout to wait for the sub-jobs to reach the next state.

        Returns:
            This `Job` object
            :param timeout_ms: Wil determine how long to wait for success
            :param polling_interval_ms: will determine how fast the API is polled for updates.
            Note that low values will produce unnecessary load.
        """
        wait_until(
            condition=lambda: self.sub_jobs_in_state(JobStates.pending) == 0,
            timeout_ms=timeout_ms,
            timeout_message=f"Timeout while waiting for sub-jobs to complete! [timeout: {timeout_ms}ms]",
            polling_interval_ms=polling_interval_ms
        )
        wait_until(
            condition=lambda: self.sub_jobs_in_state(JobStates.processing) == 0,
            timeout_ms=timeout_ms,
            timeout_message=f"Timeout while waiting for sub-jobs to complete! [timeout: {timeout_ms}ms]",
            polling_interval_ms=polling_interval_ms
        )

        error_count = self.sub_jobs_in_state(JobStates.error)
        if error_count > 0:
            raise PollingException(f"{f':Sub-jobs returned an error! {error_count} sub-jobs in state error .'}")
        return self

    def hide(self) -> Self:
        """Mark this job as hidden.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.hide_action.execute()
        self.refresh()
        return self

    def delete(self) -> Self:
        """Delete this job.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.delete_action.execute()
        self.job_hco = None
        return self

    def delete_with_associated(
            self,
            *,
            delete_output_workdata: bool = True,
            delete_input_workdata: bool = False,
            delete_subjobs_with_data: bool = True
    ) -> Self:
        """Delete this job after deleting output workdata and subjobs (recursive call) depending on the flag.
        Afterward, also deletes input workdata depending on the flag. This is a best effort operation,
        if an operation can not be executed a warning will be printed but the process continues.

        Args:
            delete_output_workdata: boolean flag to specify if output WorkData should be attempted for deletion. Default: True
            delete_input_workdata: boolean flag to specify if input WorkData should be attempted for deletion. Default: False
            delete_subjobs_with_data: boolean flag tp specify if Sub jobs should be attempted for deletion. Default: True

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()

        # delete subjobs
        if delete_subjobs_with_data is True:
            for subjob in self._get_sub_jobs().iter_flat():
                try:
                    # recursion
                    subjob_wrapper = Job.from_hco(subjob)
                    subjob_wrapper.delete_with_associated(
                        delete_output_workdata=delete_output_workdata,
                        delete_input_workdata=delete_input_workdata,
                        delete_subjobs_with_data=delete_subjobs_with_data)
                    if subjob.self_link.exists():
                        warnings.warn(f"Could not delete subjob: {subjob.self_link.get_url()}")
                except (ClientException, ApiException) as e:
                    warnings.warn(f"Could not delete subjob: {subjob.self_link.get_url()}\n{e}")
                    pass
        self.refresh()

        # delete output workdatas
        if delete_output_workdata is True:
            for slot in self.job_hco.output_dataslots:
                for wd in slot.assigned_workdatas:
                    try:
                        if wd.delete_action.is_available():
                            wd.delete_action.execute()
                        else:
                            warnings.warn(f"Could not delete output workdata: {wd.self_link.get_url()}")
                    except (ClientException, ApiException) as e:
                        warnings.warn(f"Could not delete output workdata: {wd.self_link.get_url()}\n{e}")
                        pass

        # delete this job
        self.refresh()

        job_was_deleted = False
        try:
            if self.job_hco.delete_action.is_available():
                self.job_hco.delete_action.execute()
                # do not delete the hco here since we want to access its data slots just below
                job_was_deleted = True

            else:
                warnings.warn(f"Could not delete job: {self.self_link().get_url()}")
        except (ClientException, ApiException) as e:
            warnings.warn(f"Could not delete job: {self.self_link().get_url()}\n{e}")

        # finally delete input workdatas
        if delete_input_workdata is True:
            for slot in self.job_hco.input_dataslots:
                for wd in slot.selected_workdatas:
                    try:
                        wd = wd.self_link.navigate()
                        if wd.delete_action.is_available():
                            wd.delete_action.execute()
                        else:
                            warnings.warn(f"Could not delete input workdata: {wd.self_link.get_url()}")
                    except (ClientException, ApiException) as e:
                        warnings.warn(f"Could not delete input workdata: {wd.self_link.get_url()}\n{e}")
                        pass

        # we are done with the hco, set to none now since the resource was deleted. The wrapper makes no sense anymore
        if job_was_deleted:
            self.job_hco = None
        return self

    def unhide(self) -> Self:
        """Reveal this job again.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.unhide_action.execute()
        self.refresh()
        return self

    def allow_output_data_deletion(self) -> Self:
        """Mark all output workdata from this job as "deletable".

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.allow_output_data_deletion_action.execute()
        self.refresh()
        return self

    def disallow_output_data_deletion(self) -> Self:
        """Mark all output workdata from this job as "not deletable".

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.disallow_output_data_deletion_action.execute()
        self.refresh()
        return self

    def set_tags(self, tags: list[str]) -> Self:
        """Set tags to the job.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.edit_tags_action.execute(
            SetJobTagsParameters(tags=tags)
        )
        self.refresh()
        return self

    def get_input_data_slots(self) -> list[InputDataSlotHco]:
        """Returns list of InputDataSlotHco objects.

        Returns:
            `list[InputDataSlotHco]` object
        """
        self._raise_if_no_hco()
        return self.job_hco.input_dataslots

    def get_output_data_slots(self) -> list[OutputDataSlotHco]:
        """Returns list of OutputDataSlotHco objects.

        Returns:
            `list[OutputDataSlotHco]` object
        """
        self._raise_if_no_hco()
        return self.job_hco.output_dataslots

    def get_processing_info(self) -> ProcessingView:
        self._raise_if_no_hco()
        return self.job_hco.processing

    def create_and_configure_rapidly(
            self,
            *,
            name: str,
            parent_job_url: JobLink | None = None,
            parent_job_instance: Self | None = None,
            tags: list[str] | None = None,
            processing_step_url: ProcessingStepLink | None = None,
            processing_step_instance: ProcessingStep | None = None,
            start: bool = True,
            parameters: str | None = None,
            allow_output_data_slots: bool | None = None,
            input_data_slots: List[InputDataSlotParameterFlexible] | None = None,
    ) -> Self:
        """
        Creates a new job and configures it rapidly with RapidJobSetupParameters.

        Args:
            parameters: The parameters to configure the job with.

        Returns:
            The newly created job as `Job` object
        """

        # handle parent job
        if sum(p is not None for p in [parent_job_url, parent_job_instance]) > 1:
            raise ValueError("Either none or at most 1 one of parent_job_url or parent_job_instance must be provided")
        parent_job = None
        if parent_job_instance is not None:
            if not isinstance(parent_job_instance, Job):
                raise Exception('Instance passed to "parent_job_instance" is not of type "Job"')
            parent_job = parent_job_instance.self_link().get_url()
        elif parent_job_url is not None:
            if not isinstance(parent_job_url, JobLink):
                raise Exception('Instance passed to "parent_job_url" is not of type "JobLink"')
            parent_job = parent_job_url.get_url()

        # handle processing step
        if sum(p is not None for p in [processing_step_url, processing_step_instance]) != 1:
            raise ValueError("Exactly one of processing_step_url or processing_step_instance must be provided")
        if processing_step_instance is not None:
            if not isinstance(processing_step_instance, ProcessingStep):
                raise Exception('Instance passed to "processing_step_instance" is not of type "ProcessingStep"')
            processing_step = processing_step_instance.self_link().get_url()
        else:
            if not isinstance(processing_step_url, ProcessingStepLink):
                raise Exception('Instance passed to "processing_step_url" is not of type "ProcessingStepLink"')
            processing_step = processing_step_url.get_url()

        # handle input data slots
        if input_data_slots is not None:
            input_data_slots = [
                InputDataSlotParameter(
                    Index=slot.index,
                    WorkDataUrls=slot.work_data_urls
                ) for slot in input_data_slots
            ]

        # build RapidJobSetupParameters
        params = RapidJobSetupParameters(
            Name=name,
            ParentJobUrl=None if parent_job is None else str(parent_job),
            ProcessingStepUrl=str(processing_step),
            Tags=tags,
            Start=start,
            Parameters=parameters,
            AllowOutputDataDeletion=allow_output_data_slots,
            InputDataSlots=input_data_slots
        )

        job_link = self._jobs_root.rapid_job_setup_action.execute(params)
        self._get_by_link(job_link)
        return self

    def self_link(self) -> JobLink:
        self._raise_if_no_hco()
        return self.job_hco.self_link

    def set_to_error_state(self) -> Self:
        """Set this job to error state.

        Returns:
            This `Job` object
        """
        self._raise_if_no_hco()
        self.job_hco.set_to_error_state_action.execute()
        return self

    def _raise_if_no_hco(self):
        if self.job_hco is None:
            raise Exception("No job hco present. Maybe this class is used after resource deletion.")
