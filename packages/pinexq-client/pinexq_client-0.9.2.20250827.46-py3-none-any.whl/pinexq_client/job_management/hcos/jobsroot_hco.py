from typing import Self

import httpx
from httpx import URL

from pinexq_client.core import MediaTypes, Link
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.hco_base import Hco
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableAction, UnavailableLink
from pinexq_client.job_management.hcos.job_hco import JobLink
from pinexq_client.job_management.hcos.job_query_result_hco import (
    JobQueryResultHco,
    JobQueryResultLink
)
from pinexq_client.job_management.hcos.job_used_tags_hco import JobUsedTagsLink
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import RapidJobSetupParameters
from pinexq_client.job_management.model.open_api_generated import (
    CreateJobParameters,
    JobQueryParameters,
    CreateSubJobParameters
)
from pinexq_client.job_management.model.sirenentities import JobsRootEntity


class CreateJobAction(ActionWithParametersHco[CreateJobParameters]):
    def execute(self, parameters: CreateJobParameters) -> JobLink:
        url: URL = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Created job", MediaTypes.SIREN)
        return JobLink.from_link(self._client, link)

    def default_parameters(self) -> CreateJobParameters:
        return self._get_default_parameters(CreateJobParameters, CreateJobParameters())


class CreateSubJobAction(ActionWithParametersHco[CreateSubJobParameters]):
    def execute(self, parameters: CreateSubJobParameters) -> JobLink:
        url = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Created sub-job", MediaTypes.SIREN)
        return JobLink.from_link(self._client, link)

    def default_parameters(self) -> CreateSubJobParameters:
        return self._get_default_parameters(CreateSubJobParameters, CreateSubJobParameters())


class RapidJobSetupAction(ActionWithParametersHco[RapidJobSetupParameters]):
    def execute(self, parameters: RapidJobSetupParameters) -> JobLink:
        url: URL = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Rapid job setup", MediaTypes.SIREN)
        return JobLink.from_link(self._client, link)

    def default_parameters(self) -> RapidJobSetupParameters:
        return self._get_default_parameters(RapidJobSetupParameters, RapidJobSetupParameters())


class JobQueryAction(ActionWithParametersHco):
    def execute(self, parameters: JobQueryParameters) -> JobQueryResultHco:
        url = self._execute_returns_url(parameters)
        link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Created job query", MediaTypes.SIREN)
        # resolve link immediately
        return JobQueryResultLink.from_link(self._client, link).navigate()

    def default_parameters(self) -> JobQueryParameters:
        return self._get_default_parameters(JobQueryParameters, JobQueryParameters())


class JobsRootHco(Hco[JobsRootEntity]):
    create_job_action: CreateJobAction | UnavailableAction
    rapid_job_setup_action: RapidJobSetupAction | UnavailableAction
    job_query_action: JobQueryAction | UnavailableAction
    create_subjob_action: CreateSubJobAction | UnavailableAction
    used_tags_link: JobUsedTagsLink | UnavailableLink

    self_link: 'JobsRootLink'

    @classmethod
    def from_entity(cls, entity: JobsRootEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["JobsRoot"])
        instance.create_job_action = CreateJobAction.from_entity_optional(client, instance._entity, "CreateJob")
        instance.create_subjob_action = CreateSubJobAction.from_entity_optional(client, instance._entity,
                                                                                "CreateSubJob")
        instance.rapid_job_setup_action = RapidJobSetupAction.from_entity_optional(client, instance._entity,
                                                                                   "RapidSetupJob")
        instance.job_query_action = JobQueryAction.from_entity_optional(client, instance._entity, "CreateJobQuery")
        instance.used_tags_link = JobUsedTagsLink.from_entity_optional(
            instance._client, instance._entity, Relations.USED_TAGS)
        instance.self_link = JobsRootLink.from_entity(instance._client, instance._entity, Relations.SELF)

        return instance


class JobsRootLink(LinkHco):
    def navigate(self) -> JobsRootHco:
        return JobsRootHco.from_entity(self._navigate_internal(JobsRootEntity), self._client)
