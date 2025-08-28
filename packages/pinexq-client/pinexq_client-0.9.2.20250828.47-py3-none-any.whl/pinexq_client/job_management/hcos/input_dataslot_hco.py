from typing import Self

import httpx

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.action_hco import ActionHco
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.core.hco.unavailable import UnavailableAction
from pinexq_client.core.hco.upload_action_hco import UploadAction, UploadParameters
from pinexq_client.job_management.hcos.workdata_hco import WorkDataLink, WorkDataHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.open_api_generated import SelectWorkDataForDataSlotParameters, \
	SelectWorkDataCollectionForDataSlotParameters
from pinexq_client.job_management.model.sirenentities import InputDataSlotEntity, WorkDataEntity


class InputDataSlotLink(LinkHco):
	def navigate(self) -> 'InputDataSlotHco':
		return InputDataSlotHco.from_entity(self._navigate_internal(InputDataSlotEntity), self._client)


class InputDataSlotSelectWorkDataAction(ActionWithParametersHco[SelectWorkDataForDataSlotParameters]):
	def execute(self, parameters: SelectWorkDataForDataSlotParameters):
		self._execute(parameters)


class InputDataSlotSelectWorkDataCollectionAction(
	ActionWithParametersHco[SelectWorkDataCollectionForDataSlotParameters]):
	def execute(self, parameters: SelectWorkDataCollectionForDataSlotParameters):
		self._execute(parameters)


class InputDataSlotUploadWorkDataAction(UploadAction):
	def execute(self, parameters: UploadParameters) -> WorkDataLink:
		url = self._upload(parameters)
		link = Link.from_url(url, [str(Relations.CREATED_RESSOURCE)], "Uploaded workdata", MediaTypes.SIREN)
		return WorkDataLink.from_link(self._client, link)


class InputDataSlotClearDataAction(ActionHco):
	def execute(self):
		self._execute_internal()


class InputDataSlotHco(Hco[InputDataSlotEntity]):
	is_configured: bool | None = Property()
	title: str | None = Property()
	description: str | None = Property()
	media_type: str | None = Property()
	selected_workdatas: list[WorkDataHco]

	select_workdata_action: InputDataSlotSelectWorkDataAction | UnavailableAction
	select_workdata_collection_action: InputDataSlotSelectWorkDataCollectionAction | UnavailableAction
	clear_workdata_action: InputDataSlotClearDataAction | UnavailableAction

	@classmethod
	def from_entity(cls, entity: InputDataSlotEntity, client: httpx.Client) -> Self:
		instance = cls(client, entity)
		Hco.check_classes(instance._entity.class_, ["InputDataSlot"])

		# actions
		instance.select_workdata_action = InputDataSlotSelectWorkDataAction.from_entity_optional(
			client, instance._entity, "SelectWorkData")
		instance.select_workdata_collection_action = InputDataSlotSelectWorkDataCollectionAction.from_entity_optional(
			client, instance._entity, "SelectWorkDataCollection")
		instance.clear_workdata_action = InputDataSlotClearDataAction.from_entity_optional(
			client, instance._entity, "Clear")

		instance._extract_workdata()

		return instance

	def _extract_workdata(self):
		self.selected_workdatas = []

		workdatas: list[WorkDataEntity] = self._entity.find_all_entities_with_relation(Relations.SELECTED,
																					   WorkDataEntity)
		if not workdatas:
			return

		self.selected_workdatas = [WorkDataHco.from_entity(workdata, self._client)
								   for workdata in workdatas]
