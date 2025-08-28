from typing import Self

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.hcos.workdata_hco import WorkDataHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import (
    OutputDataSlotEntity,
    WorkDataEntity
)


class OutputDataSlotLink(LinkHco):
    def navigate(self) -> 'OutputDataSlotHco':
        return OutputDataSlotHco.from_entity(self._navigate_internal(OutputDataSlotEntity), self._client)


class OutputDataSlotHco(Hco[OutputDataSlotEntity]):
    title: str | None = Property()
    description: str | None = Property()
    media_type: str | None = Property()
    assigned_workdatas: list[WorkDataHco]

    @classmethod
    def from_entity(cls, entity: OutputDataSlotEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)
        Hco.check_classes(instance._entity.class_, ["OutputDataSlot"])

        instance._extract_workdata()

        return instance

    def _extract_workdata(self):
        self.assigned_workdatas = []

        workdatas: list[WorkDataEntity] = self._entity.find_all_entities_with_relation(Relations.ASSIGNED,
                                                                                       WorkDataEntity)
        if not workdatas:
            return

        self.assigned_workdatas = [WorkDataHco.from_entity(workdata, self._client)
                                   for workdata in workdatas]
