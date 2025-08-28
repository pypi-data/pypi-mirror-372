from datetime import datetime
from typing import Self

import httpx

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.action_hco import ActionHco
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.download_link_hco import DownloadLinkHco
from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableAction, UnavailableLink
from pinexq_client.job_management.hcos.processing_step_hco import ProcessingStepLink
from pinexq_client.job_management.hcos.job_hco import JobLink
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import CopyWorkDataFromUserToOrgActionParameters
from pinexq_client.job_management.model.open_api_generated import (
    SetNameWorkDataParameters,
    SetCommentWorkDataParameters,
    SetTagsWorkDataParameters,
    WorkDataKind
)
from pinexq_client.job_management.model.sirenentities import WorkDataEntity


class WorkDataLink(LinkHco):
    def navigate(self) -> 'WorkDataHco':
        return WorkDataHco.from_entity(self._navigate_internal(WorkDataEntity), self._client)


class WorkDataDeleteAction(ActionHco):
    def execute(self):
        self._execute_internal()


class WorkDataRenameAction(ActionWithParametersHco[SetNameWorkDataParameters]):
    def execute(self, parameters: SetNameWorkDataParameters):
        self._execute(parameters)

    def default_parameters(self) -> SetNameWorkDataParameters:
        return self._get_default_parameters(SetNameWorkDataParameters, SetNameWorkDataParameters())


class WorkDataEditCommentAction(ActionWithParametersHco[SetCommentWorkDataParameters]):
    def execute(self, parameters: SetCommentWorkDataParameters):
        self._execute(parameters)

    def default_parameters(self) -> SetCommentWorkDataParameters:
        return self._get_default_parameters(SetCommentWorkDataParameters, SetCommentWorkDataParameters())


class WorkDataEditTagsAction(ActionWithParametersHco[SetTagsWorkDataParameters]):
    def execute(self, parameters: SetTagsWorkDataParameters):
        self._execute(parameters)

    def default_parameters(self) -> SetTagsWorkDataParameters:
        # todo check why we have to manually set tags
        return self._get_default_parameters(SetTagsWorkDataParameters, SetTagsWorkDataParameters(tags=[]))


class WorkDataAllowDeletionAction(ActionHco):
    def execute(self):
        self._execute_internal()


class WorkDataDisallowAction(ActionHco):
    def execute(self):
        self._execute_internal()


class WorkDataHideAction(ActionHco):
    def execute(self):
        self._execute_internal()


class WorkDataUnHideAction(ActionHco):
    def execute(self):
        self._execute_internal()


class WorkDataCopyUserToOrgAction(ActionWithParametersHco[CopyWorkDataFromUserToOrgActionParameters]):
    def execute(self, parameters: CopyWorkDataFromUserToOrgActionParameters) -> WorkDataLink:
        url = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Copied workdata", MediaTypes.SIREN)
        return WorkDataLink.from_link(self._client, link)

    def default_parameters(self) -> CopyWorkDataFromUserToOrgActionParameters:
        return self._get_default_parameters(CopyWorkDataFromUserToOrgActionParameters, CopyWorkDataFromUserToOrgActionParameters())


class WorkDataCopyOrgToUserAction(ActionHco):
    def execute(self) -> WorkDataLink:
        url = self._execute_internal()
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Copied workdata", MediaTypes.SIREN)
        return WorkDataLink.from_link(self._client, link)


class WorkDataHco(Hco[WorkDataEntity]):
    name: str | None = Property()
    created_at: datetime | None = Property()
    size_in_bytes: int | None = Property()
    tags: list[str] | None = Property()
    media_type: str | None = Property()
    kind: WorkDataKind | None = Property()
    comments: str | None = Property()
    is_deletable: bool | None = Property()
    hidden: bool | None = Property()

    delete_action: WorkDataDeleteAction | UnavailableAction
    hide_action: WorkDataHideAction | UnavailableAction
    unhide_action: WorkDataUnHideAction | UnavailableAction
    allow_deletion_action: WorkDataAllowDeletionAction | UnavailableAction
    disallow_deletion_action: WorkDataDisallowAction | UnavailableAction
    rename_action: WorkDataRenameAction | UnavailableAction
    edit_comment_action: WorkDataEditCommentAction | UnavailableAction
    edit_tags_action: WorkDataEditTagsAction | UnavailableAction
    copy_user_to_org_action: WorkDataCopyUserToOrgAction | UnavailableAction
    copy_org_to_user_action: WorkDataCopyOrgToUserAction | UnavailableAction

    self_link: WorkDataLink
    download_link: DownloadLinkHco
    producer_job_link: JobLink | UnavailableLink
    producer_processing_step_link: ProcessingStepLink | UnavailableLink

    @classmethod
    def from_entity(cls, entity: WorkDataEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)
        Hco.check_classes(instance._entity.class_, ["WorkData"])

        # actions
        instance.hide_action = WorkDataHideAction.from_entity_optional(
            client, instance._entity, "Hide")
        instance.unhide_action = WorkDataUnHideAction.from_entity_optional(
            client, instance._entity, "UnHide")
        instance.delete_action = WorkDataDeleteAction.from_entity_optional(
            client, instance._entity, "Delete")
        instance.rename_action = WorkDataRenameAction.from_entity_optional(
            client, instance._entity, "Rename")
        instance.edit_comment_action = WorkDataEditCommentAction.from_entity_optional(
            client, instance._entity, "EditComment")
        instance.edit_tags_action = WorkDataEditTagsAction.from_entity_optional(
            client, instance._entity, "EditTags")
        instance.allow_deletion_action = WorkDataAllowDeletionAction.from_entity_optional(
            client, instance._entity, "AllowDeletion")
        instance.disallow_deletion_action = WorkDataDisallowAction.from_entity_optional(
            client, instance._entity, "DisallowDeletion")
        instance.copy_user_to_org_action = WorkDataCopyUserToOrgAction.from_entity_optional(
            client, instance._entity, "CopyToOrg")
        instance.copy_org_to_user_action = WorkDataCopyOrgToUserAction.from_entity_optional(
            client, instance._entity, "CopyToUser")

        # links
        instance.self_link = WorkDataLink.from_entity(
            instance._client, instance._entity, Relations.SELF)
        instance.download_link = DownloadLinkHco.from_entity(
            instance._client, instance._entity, Relations.DOWNLOAD)
        instance.producer_job_link = JobLink.from_entity_optional(
            instance._client, instance._entity, Relations.PRODUCED_BY_JOB)
        instance.producer_processing_step_link = ProcessingStepLink.from_entity_optional(
            instance._client, instance._entity, Relations.PRODUCED_BY_PROCESSING_STEP)
        return instance
