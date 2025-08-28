from typing import Self, List, Iterator

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableLink
from pinexq_client.job_management.hcos.processing_step_hco import ProcessingStepHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import (
	ProcessingStepQueryResultEntity,
	ProcessingStepEntity
)


class ProcessingStepQueryResultPaginationLink(LinkHco):
	def navigate(self) -> 'ProcessingStepQueryResultHco':
		return ProcessingStepQueryResultHco.from_entity(self._navigate_internal(ProcessingStepQueryResultEntity),
														self._client)


class ProcessingStepQueryResultLink(LinkHco):
	def navigate(self) -> 'ProcessingStepQueryResultHco':
		return ProcessingStepQueryResultHco.from_entity(self._navigate_internal(ProcessingStepQueryResultEntity),
														self._client)


class ProcessingStepQueryResultHco(Hco[ProcessingStepQueryResultEntity]):
	total_entities: int = Property()
	current_entities_count: int = Property()
	processing_steps: list[ProcessingStepHco]
	remaining_tags: List[str] | None = Property()

	self_link: ProcessingStepQueryResultLink
	all_link: ProcessingStepQueryResultPaginationLink | UnavailableLink
	first_link: ProcessingStepQueryResultPaginationLink | UnavailableLink
	last_link: ProcessingStepQueryResultPaginationLink | UnavailableLink
	next_link: ProcessingStepQueryResultPaginationLink | UnavailableLink
	previous_link: ProcessingStepQueryResultPaginationLink | UnavailableLink

	@classmethod
	def from_entity(cls, entity: ProcessingStepQueryResultEntity, client: httpx.Client) -> Self:
		instance = cls(client, entity)

		Hco.check_classes(instance._entity.class_, ["ProcessingStepQueryResult"])

		# pagination links
		instance.self_link = ProcessingStepQueryResultLink.from_entity(
			instance._client, instance._entity, Relations.SELF)
		instance.all_link = ProcessingStepQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.ALL)
		instance.first_link = ProcessingStepQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.FIRST)
		instance.last_link = ProcessingStepQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.LAST)
		instance.next_link = ProcessingStepQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.NEXT)
		instance.previous_link = ProcessingStepQueryResultPaginationLink.from_entity_optional(
			instance._client, instance._entity, Relations.PREVIOUS)

		instance._extract_processing_steps()

		return instance

	def _extract_processing_steps(self):
		self.processing_steps = []
		processing_steps = self._entity.find_all_entities_with_relation(Relations.ITEM, ProcessingStepEntity)
		for processing_step in processing_steps:
			processing_step_hco: ProcessingStepHco = ProcessingStepHco.from_entity(processing_step, self._client)
			self.processing_steps.append(processing_step_hco)

	def iter(self) -> Iterator[Self]:
		"""
		Returns an Iterator of `ProcessingStepQueryResultHco` objects so that all pages can be processed in a loop.

		Returns:
			An iterator of `ProcessingStepQueryResultHco` objects
		"""
		result = self
		while result is not None:
			yield result
			if isinstance(result.next_link, UnavailableLink):
				return
			result = result.next_link.navigate()

	def iter_flat(self) -> Iterator[ProcessingStepHco]:
		"""
		Returns an Iterator of `ProcessingStepHco` objects so that all processing steps can be processed in a loop.

		Returns:
			An iterator of `ProcessingStepHco` objects
		"""
		for page in self.iter():
			yield from page.processing_steps
