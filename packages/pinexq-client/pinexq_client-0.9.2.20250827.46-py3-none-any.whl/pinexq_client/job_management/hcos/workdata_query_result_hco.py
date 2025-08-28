from typing import Self, List, Iterator

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableLink
from pinexq_client.job_management.hcos.workdata_hco import WorkDataHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import WorkDataQueryResultEntity, WorkDataEntity


class WorkDataQueryResultPaginationLink(LinkHco):
	def navigate(self) -> 'WorkDataQueryResultHco':
		return WorkDataQueryResultHco.from_entity(self._navigate_internal(WorkDataQueryResultEntity), self._client)


class WorkDataQueryResultLink(LinkHco):
	def navigate(self) -> 'WorkDataQueryResultHco':
		return WorkDataQueryResultHco.from_entity(self._navigate_internal(WorkDataQueryResultEntity), self._client)


class WorkDataQueryResultHco(Hco[WorkDataQueryResultEntity]):
	workdata_query_action: WorkDataQueryResultEntity

	total_entities: int = Property()
	current_entities_count: int = Property()
	workdatas: list[WorkDataHco]
	remaining_tags: List[str] | None = Property()

	self_link: WorkDataQueryResultLink
	all_link: WorkDataQueryResultPaginationLink | UnavailableLink
	first_link: WorkDataQueryResultPaginationLink | UnavailableLink
	last_link: WorkDataQueryResultPaginationLink | UnavailableLink
	next_link: WorkDataQueryResultPaginationLink | UnavailableLink
	previous_link: WorkDataQueryResultPaginationLink | UnavailableLink

	@classmethod
	def from_entity(cls, entity: WorkDataQueryResultEntity, client: httpx.Client) -> Self:
		instance = cls(client, entity)

		Hco.check_classes(instance._entity.class_, ["WorkDataQueryResult"])

		# pagination links
		instance.self_link = WorkDataQueryResultLink.from_entity(
			instance._client, instance._entity, Relations.SELF)
		instance.all_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.ALL)
		instance.first_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.FIRST)
		instance.last_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.LAST)
		instance.next_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.NEXT)
		instance.previous_link = WorkDataQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.PREVIOUS)

		# entities

		instance._extract_workdatas()

		return instance

	def _extract_workdatas(self):
		self.workdatas = []
		workdatas = self._entity.find_all_entities_with_relation(Relations.ITEM, WorkDataEntity)
		for workdata in workdatas:
			workdata_hco: WorkDataHco = WorkDataHco.from_entity(workdata, self._client)
			self.workdatas.append(workdata_hco)

	def iter(self) -> Iterator[Self]:
		"""
		Returns an Iterator of `WorkDataQueryResultHco` so that all pages can be processed in a loop.
		Returns:
			An iterator of `WorkDataQueryResultHco` objects
		"""
		result = self
		while result is not None:
			yield result
			if isinstance(result.next_link, UnavailableLink):
				return
			result = result.next_link.navigate()

	def iter_flat(self) -> Iterator[WorkDataHco]:
		"""
		Returns an Iterator of the `WorkDataHco` so that all WorkDatas can be processed in a loop.
		Returns:
			An iterator of `WorkDataHco` objects
		"""
		for page in self.iter():
			yield from page.workdatas
