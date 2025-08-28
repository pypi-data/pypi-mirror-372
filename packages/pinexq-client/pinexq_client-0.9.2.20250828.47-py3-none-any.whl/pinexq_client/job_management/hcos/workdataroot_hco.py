from typing import Self

import httpx

from pinexq_client.core import MediaTypes, Link
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.hco_base import Hco
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableAction, UnavailableLink
from pinexq_client.core.hco.upload_action_hco import UploadAction, UploadParameters
from pinexq_client.job_management.hcos.workdata_hco import WorkDataLink
from pinexq_client.job_management.hcos.workdata_query_result_hco import (
	WorkDataQueryResultHco,
	WorkDataQueryResultLink,
	WorkDataQueryResultPaginationLink
)
from pinexq_client.job_management.hcos.workdata_used_tags_query_result_hco import WorkDataUsedTagsLink
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import WorkDataQueryParameters, WorkDataUsedTagsFilterParameter
from pinexq_client.job_management.model.sirenentities import WorkDataRootEntity


class WorkDataQueryAction(ActionWithParametersHco[WorkDataQueryParameters]):
	def execute(self, parameters: WorkDataQueryParameters) -> WorkDataQueryResultHco:
		url = self._execute_returns_url(parameters)
		link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Created query", MediaTypes.SIREN)
		# resolve link immediately
		return WorkDataQueryResultLink.from_link(self._client, link).navigate()

	def default_parameters(self) -> WorkDataQueryParameters:
		return self._get_default_parameters(WorkDataQueryParameters, WorkDataQueryParameters())


class WorkDataUsedTagsQueryAction(ActionWithParametersHco[WorkDataUsedTagsFilterParameter]):
	def execute(self, parameters: WorkDataUsedTagsFilterParameter) -> WorkDataUsedTagsLink:
		url = self._execute_returns_url(parameters)
		link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Created query", MediaTypes.SIREN)
		return WorkDataUsedTagsLink.from_link(self._client, link)

	def default_parameters(self) -> WorkDataUsedTagsFilterParameter:
		return self._get_default_parameters(WorkDataUsedTagsFilterParameter, WorkDataUsedTagsFilterParameter())


class WorkDataUploadAction(UploadAction):
	def execute(self, parameters: UploadParameters) -> WorkDataLink:
		url = self._upload(parameters)
		link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Uploaded workdata", MediaTypes.SIREN)
		return WorkDataLink.from_link(self._client, link)


class WorkDataRootLink(LinkHco):
	def navigate(self) -> 'WorkDataRootHco':
		return WorkDataRootHco.from_entity(self._navigate_internal(WorkDataRootEntity), self._client)


class WorkDataRootHco(Hco[WorkDataRootEntity]):
	query_action: WorkDataQueryAction | UnavailableAction
	query_tags_action: WorkDataUsedTagsQueryAction | UnavailableAction
	upload_action: WorkDataUploadAction | None

	self_link: WorkDataRootLink
	all_link: WorkDataQueryResultPaginationLink | UnavailableLink
	used_tags_link: WorkDataUsedTagsLink | UnavailableLink

	@classmethod
	def from_entity(cls, entity: WorkDataRootEntity, client: httpx.Client) -> Self:
		instance = cls(client, entity)
		Hco.check_classes(instance._entity.class_, ["WorkDataRoot"])

		instance.query_action = WorkDataQueryAction.from_entity_optional(
			client, instance._entity, "CreateWorkDataQuery")
		instance.query_tags_action = WorkDataUsedTagsQueryAction.from_entity_optional(
			client, instance._entity, "CreateWorkDataTagsQuery")
		instance.upload_action = WorkDataUploadAction.from_entity_optional(
			client, instance._entity, "Upload")

		instance.self_link = WorkDataRootLink.from_entity(
			instance._client, instance._entity, Relations.SELF)

		instance.all_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.ALL)

		instance.used_tags_link = WorkDataUsedTagsLink.from_entity_optional(
			instance._client, instance._entity, Relations.USED_TAGS)
		return instance
