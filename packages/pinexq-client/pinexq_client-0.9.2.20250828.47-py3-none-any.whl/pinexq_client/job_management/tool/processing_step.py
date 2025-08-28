from typing import Any, Self, Optional

import httpx
from httpx import URL

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.upload_action_hco import UploadParameters
from pinexq_client.job_management.enterjma import enter_jma
from pinexq_client.job_management.hcos import ProcessingStepHco, ProcessingStepLink, ProcessingStepQueryResultHco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.hcos.job_hco import GenericProcessingConfigureParameters
from pinexq_client.job_management.hcos.processingsteproot_hco import ProcessingStepsRootHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import (
    CreateProcessingStepParameters,
    SetProcessingStepTagsParameters, ProcessingStepQueryParameters, ProcessingStepFilterParameter,
    FunctionNameMatchTypes, EditProcessingStepParameters, CopyPsFromUserToOrgActionParameters,
    CopyPsFromOrgToUserActionParameters,
)


class ProcessingStep:
    """Convenience wrapper for handling ProcessingStepHcos in the JobManagement-Api.
    """

    _client: httpx.Client
    _entrypoint: EntryPointHco
    _processing_steps_root: ProcessingStepsRootHco
    processing_step_hco: ProcessingStepHco | None = None # Internal hco of the wrapper. This is updated by this class. You should not take a reference to this object.


    def __init__(self, client: httpx.Client):
        """

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
        """
        self._client = client
        self._entrypoint = enter_jma(client)
        self._processing_steps_root = self._entrypoint.processing_step_root_link.navigate()

    def create(self, title: str, function_name: str, version: str = "0") -> Self:
        """
        Creates a new ProcessingStep by name.

        Args:
            title: Title of the ProcessingStep to be created
            function_name: Function name of the ProcessingStep to be created
            version: Version of the ProcessingStep to be created

        Returns:
            The newly created ProcessingStep as `ProcessingStep` object
        """
        processing_step_hco = self._processing_steps_root.register_new_action.execute(CreateProcessingStepParameters(
            title=title,
            function_name=function_name,
            version=version
        ))
        self.processing_step_hco = processing_step_hco
        return self

    def _get_by_link(self, processing_step_link: ProcessingStepLink):
        self.processing_step_hco = processing_step_link.navigate()

    @classmethod
    def from_hco(cls, processing_step: ProcessingStepHco) -> Self:
        """Initializes a `ProcessingStep` object from an existing ProcessingStepHco object.

        Args:
            processing_step: The 'ProcessingStepHco' to initialize this ProcessingStep from.

        Returns:
            The newly created processing step as `ProcessingStep` object.
        """
        processing_step_instance = cls(processing_step._client)
        processing_step_instance.processing_step_hco = processing_step
        return processing_step_instance

    @classmethod
    def from_url(cls, client: httpx.Client, processing_step_url: URL) -> Self:
        """Initializes a `ProcessingStep` object from an existing processing step given by its link as URL.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            processing_step_url: The URL of the processing step

        Returns:
            The newly created processing step as `ProcessingStep` object
        """
        link = Link.from_url(
            processing_step_url,
            [str(Relations.CREATED_RESSOURCE)],
            "Created processing step",
            MediaTypes.SIREN,
        )
        processing_step_instance = cls(client)
        processing_step_instance._get_by_link(ProcessingStepLink.from_link(client, link))
        return processing_step_instance

    @classmethod
    def from_name(cls, client: httpx.Client, step_name: str, version: str = "0") -> Self:
        """Create a ProcessingStep object from an existing name.

        Args:
            client: Create a ProcessingStep object from an existing name.
            step_name: Name of the registered processing step.
            version: Version of the ProcessingStep to be created

        Returns:
            The newly created processing step as `ProcessingStep` object
        """

        # Attempt to find the processing step
        query_result = cls._query_processing_steps(client, step_name, version)

        # Check if exactly one result is found
        if len(query_result.processing_steps) != 1:
            # Attempt to suggest alternative steps if exact match not found
            suggested_steps = cls._processing_steps_by_name(client, step_name)
            raise NameError(
                f"No processing step with the name {step_name} and version {version} registered. "
                f"Suggestions: {suggested_steps}"
            )

        # Todo: For now we choose the first and only result. Make this more flexible?
        processing_step_hco = query_result.processing_steps[0]
        return ProcessingStep.from_hco(processing_step_hco)

    @staticmethod
    def _query_processing_steps(client: httpx.Client, step_name: str,
                                version: Optional[str] = None) -> ProcessingStepQueryResultHco:
        """
        Helper function to query processing steps based on name and optional version.

        Args:
            client: HTTP client for executing queries.
            step_name: Name of the processing step.
            version: Optional version to match.

        Returns:
            Query result object containing the matching processing steps.
        """
        query_param = ProcessingStepQueryParameters(
            filter=ProcessingStepFilterParameter(
                function_name=step_name,
                function_name_match_type=FunctionNameMatchTypes.match_exact,
                version=version
            )
        )
        instance = ProcessingStep(client)
        return instance._processing_steps_root.query_action.execute(query_param)

    @staticmethod
    def _processing_steps_by_name(client: httpx.Client, step_name: str) -> list:
        """
        Suggest processing steps if the exact step is not found.

        Args:
            client: HTTP client for executing queries.
            step_name: Name of the processing step.

        Returns:
            A list of alternative processing steps matching the step name.
        """
        # Query for steps without  version to get suggestions
        instance = ProcessingStep(client)
        query_result = instance._query_processing_steps(client, step_name)

        # If no suggestions are found, raise an error
        if len(query_result.processing_steps) == 0:
            raise NameError(f"No processing steps found with the name '{step_name}'.")

        # Return list of alternative steps as suggestions
        return [f"{step.function_name}:{step.version}" for step in query_result.processing_steps]

    def refresh(self) -> Self:
        """Updates the processing step from the server

        Returns:
            This `ProcessingStep` object, but with updated properties.
        """
        self._raise_if_no_hco()
        self.processing_step_hco = self.processing_step_hco.self_link.navigate()
        return self

    def set_tags(self, tags: list[str]) -> Self:
        """Set tags to the processing step.

        Returns:
            This `ProcessingStep` object"""
        self._raise_if_no_hco()
        self.processing_step_hco.edit_tags_action.execute(SetProcessingStepTagsParameters(
            tags=tags
        ))
        self.refresh()
        return self

    def edit_properties(
            self,
            *,
            new_title: str | None = None,
            is_public: bool | None = None,
            new_function_name: str | None = None,
            new_version: str | None = None,
    ) -> Self:
        """Edit processing step properties.

        Returns:
            This `ProcessingStep` object"""
        self._raise_if_no_hco()
        self.processing_step_hco.edit_properties_action.execute(EditProcessingStepParameters(
            title=new_title,
            is_public=is_public,
            function_name=new_function_name,
            version=new_version
        ))
        self.refresh()
        return self

    def configure_default_parameters(self, **parameters: Any) -> Self:
        """Set the parameters to run the processing step with.

        Args:
            **parameters: Any keyword parameters provided will be forwarded as parameters
                to the processing step function.

        Returns:
            This `ProcessingStep` object
        """
        self._raise_if_no_hco()
        self.processing_step_hco.configure_default_parameters_action.execute(
            GenericProcessingConfigureParameters.model_validate(parameters)
        )

        self.refresh()
        return self

    def clear_default_parameters(self) -> Self:
        """Clear default parameters.

        Returns:
            This `ProcessingStep` object
        """
        self._raise_if_no_hco()
        self.processing_step_hco.clear_default_parameters_action.execute()
        self.refresh()

        return self

    def hide(self) -> Self:
        """Hide ProcessingStep.

        Returns:
            This `ProcessingStep` object"""
        self._raise_if_no_hco()
        self.processing_step_hco.hide_action.execute()
        self.refresh()
        return self

    def unhide(self) -> Self:
        """Hide ProcessingStep.

        Returns:
            This `ProcessingStep` object"""
        self._raise_if_no_hco()
        self.processing_step_hco.unhide_action.execute()
        self.refresh()
        return self

    def delete(self) -> Self:
        """Delete ProcessingStep.

        Returns:
            This `ProcessingStep` object"""
        self._raise_if_no_hco()
        self.processing_step_hco.delete_action.execute()
        self.processing_step_hco = None
        return self

    def upload_configuration(self, json_data: Any) -> Self:
        """Upload processing configuration.

        Returns:
            This `ProcessingStep` object
        """
        self._raise_if_no_hco()
        self.processing_step_hco.upload_configuration_action.execute(
            UploadParameters(
                filename="config.json",  # placeholder, jma does not care about filename
                mediatype=MediaTypes.APPLICATION_JSON,
                json=json_data
            )
        )
        self.refresh()

        return self

    def copy_from_org_to_user(self, *, title: str, function_name: str, version: str) -> ProcessingStepLink:
        """Copy ProcessingStep from organization to user.

        Args:
            title: New title for the copied ProcessingStep
            function_name: New function for the copied ProcessingStep
            version: New version for the copied ProcessingStep

        Returns:
            The URL of the copied ProcessingStep
        """
        self._raise_if_no_hco()
        return self.processing_step_hco.copy_from_org_to_user_action.execute(
            CopyPsFromOrgToUserActionParameters(
                title=title,
                function_name=function_name,
                version=version
            )
        )

    def copy_from_user_to_org(self, *, title: str, function_name: str, version: str, org_id: str) -> ProcessingStepLink:
        """Copy ProcessingStep from user to organization.

        Args:
            org_id: The ID of the organization to copy the processing step to.
            title: New title for the copied ProcessingStep
            function_name: New function for the copied ProcessingStep
            version: New version for the copied ProcessingStep

        Returns:
            The URL of the copied ProcessingStep
        """
        self._raise_if_no_hco()
        return self.processing_step_hco.copy_from_user_to_org_action.execute(
            CopyPsFromUserToOrgActionParameters(
                org_id=org_id,
                title=title,
                function_name=function_name,
                version=version
            )
        )

    def self_link(self) -> ProcessingStepLink:
        self._raise_if_no_hco()
        return self.processing_step_hco.self_link

    def _raise_if_no_hco(self):
        if self.processing_step_hco is None:
            raise Exception("No processing step hco present. Maybe this class is used after resource deletion.")
