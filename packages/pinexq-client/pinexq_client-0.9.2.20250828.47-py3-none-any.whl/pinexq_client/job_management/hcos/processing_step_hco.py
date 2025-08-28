from datetime import datetime
from typing import List, Self

import httpx
from pydantic import BaseModel, ConfigDict

from pinexq_client.core import upload_json, Link, MediaTypes
from pinexq_client.core.hco.action_hco import ActionHco
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.download_link_hco import DownloadLinkHco
from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableAction
from pinexq_client.core.hco.upload_action_hco import UploadAction, UploadParameters
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import CopyPsFromUserToOrgActionParameters, CopyPsFromOrgToUserActionParameters
from pinexq_client.job_management.model.open_api_generated import DataSpecificationHto, \
    SetProcessingStepTagsParameters, EditProcessingStepParameters
from pinexq_client.job_management.model.sirenentities import ProcessingStepEntity


class ProcessingStepLink(LinkHco):
    def navigate(self) -> 'ProcessingStepHco':
        return ProcessingStepHco.from_entity(self._navigate_internal(ProcessingStepEntity), self._client)


class ProcessingStepEditTagsAction(ActionWithParametersHco[SetProcessingStepTagsParameters]):
    def execute(self, parameters: SetProcessingStepTagsParameters):
        self._execute(parameters)

    def default_parameters(self) -> SetProcessingStepTagsParameters:
        # todo check why we have to manually set tags
        return self._get_default_parameters(SetProcessingStepTagsParameters, SetProcessingStepTagsParameters(tags=[]))


class ProcessingStepHideAction(ActionHco):
    def execute(self):
        self._execute_internal()


class ProcessingStepUnHideAction(ActionHco):
    def execute(self):
        self._execute_internal()


class ProcessingStepEditPropertiesAction(ActionWithParametersHco[EditProcessingStepParameters]):
    def execute(self, parameters: EditProcessingStepParameters):
        self._execute(parameters)

    def default_parameters(self) -> EditProcessingStepParameters:
        return self._get_default_parameters(EditProcessingStepParameters,
                                            EditProcessingStepParameters())


class GenericProcessingConfigureParameters(BaseModel):
    """Generic parameter model, that can be set with any dictionary"""
    model_config = ConfigDict(extra='allow')


class ConfigureDefaultParametersAction(ActionWithParametersHco[GenericProcessingConfigureParameters]):
    def execute(self, parameters: GenericProcessingConfigureParameters):
        self._execute(parameters)

    def default_parameters(self) -> GenericProcessingConfigureParameters:
        return self._get_default_parameters(GenericProcessingConfigureParameters,
                                            GenericProcessingConfigureParameters())


class ClearDefaultParametersAction(ActionHco):
    def execute(self):
        self._execute_internal()


class DeleteAction(ActionHco):
    def execute(self):
        self._execute_internal()


class UploadConfigurationAction(UploadAction):
    def execute(self, parameters: UploadParameters):
        upload_json(self._client, self._action, parameters.json_, parameters.filename)


class ProcessingStepCopyFromUserToOrgAction(ActionWithParametersHco[CopyPsFromUserToOrgActionParameters]):
    def execute(self, parameters: CopyPsFromUserToOrgActionParameters) -> ProcessingStepLink:
        url = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Copied Processing Step", MediaTypes.SIREN)
        return ProcessingStepLink.from_link(self._client, link)

    def default_parameters(self) -> CopyPsFromUserToOrgActionParameters:
        return self._get_default_parameters(CopyPsFromUserToOrgActionParameters,
                                            CopyPsFromUserToOrgActionParameters())


class ProcessingStepCopyFromOrgToUserAction(ActionWithParametersHco[CopyPsFromOrgToUserActionParameters]):
    def execute(self, parameters: CopyPsFromOrgToUserActionParameters) -> ProcessingStepLink:
        url = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Copied Processing Step", MediaTypes.SIREN)
        return ProcessingStepLink.from_link(self._client, link)

    def default_parameters(self) -> CopyPsFromOrgToUserActionParameters:
        return self._get_default_parameters(CopyPsFromOrgToUserActionParameters,
                                            CopyPsFromOrgToUserActionParameters())


class ProcessingStepHco(Hco[ProcessingStepEntity]):
    title: str = Property()
    version: str | None = Property()
    function_name: str | None = Property()
    short_description: str | None = Property()
    long_description: str | None = Property()
    tags: list[str] | None = Property()
    has_parameters: bool | None = Property()
    is_public: bool | None = Property()
    is_configured: bool | None = Property()
    created_at: datetime | None = Property()
    last_modified_at: datetime | None = Property()
    parameter_schema: str | None = Property()
    default_parameters: str | None = Property()
    return_schema: str | None = Property()
    error_schema: str | None = Property()
    hidden: bool | None = Property()

    input_data_slot_specification: List[DataSpecificationHto] | None = Property()
    output_data_slot_specification: List[DataSpecificationHto] | None = Property()
    edit_tags_action: ProcessingStepEditTagsAction | UnavailableAction
    edit_properties_action: ProcessingStepEditPropertiesAction | UnavailableAction
    configure_default_parameters_action: ConfigureDefaultParametersAction | UnavailableAction
    clear_default_parameters_action: ClearDefaultParametersAction | UnavailableAction
    upload_configuration_action: UploadConfigurationAction | None
    hide_action: ProcessingStepHideAction | UnavailableAction
    unhide_action: ProcessingStepUnHideAction | UnavailableAction
    copy_from_user_to_org_action: ProcessingStepCopyFromUserToOrgAction | UnavailableAction
    copy_from_org_to_user_action: ProcessingStepCopyFromOrgToUserAction | UnavailableAction
    delete_action: DeleteAction | UnavailableAction

    self_link: ProcessingStepLink
    download_link: DownloadLinkHco

    @classmethod
    def from_entity(cls, entity: ProcessingStepEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)
        Hco.check_classes(instance._entity.class_, ["ProcessingStep"])

        instance.self_link = ProcessingStepLink.from_entity(instance._client, instance._entity, Relations.SELF)
        instance.download_link = DownloadLinkHco.from_entity(instance._client, instance._entity, Relations.DOWNLOAD)

        # todo tests

        instance.edit_tags_action = ProcessingStepEditTagsAction.from_entity_optional(
            client, instance._entity, "EditTags")
        instance.edit_properties_action = ProcessingStepEditPropertiesAction.from_entity_optional(
            client, instance._entity, "EditProperties")
        instance.configure_default_parameters_action = ConfigureDefaultParametersAction.from_entity_optional(
            client, instance._entity, "ConfigureDefaultParameters")
        instance.clear_default_parameters_action = ClearDefaultParametersAction.from_entity_optional(
            client, instance._entity, "ClearDefaultParameters")
        instance.upload_configuration_action = UploadConfigurationAction.from_entity_optional(
            client, instance._entity, "Upload")
        instance.hide_action = ProcessingStepHideAction.from_entity_optional(
            client, instance._entity, "Hide")
        instance.unhide_action = ProcessingStepUnHideAction.from_entity_optional(
            client, instance._entity, "UnHide")
        instance.copy_from_user_to_org_action = ProcessingStepCopyFromUserToOrgAction.from_entity_optional(
            client, instance._entity, "CopyToOrg")
        instance.copy_from_org_to_user_action = ProcessingStepCopyFromOrgToUserAction.from_entity_optional(
            client, instance._entity, "CopyToUser")
        instance.delete_action = DeleteAction.from_entity_optional(
            client, instance._entity, "Delete")

        return instance
