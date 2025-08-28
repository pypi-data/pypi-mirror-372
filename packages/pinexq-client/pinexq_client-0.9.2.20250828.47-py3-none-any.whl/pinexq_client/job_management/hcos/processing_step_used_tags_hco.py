from typing import List, Self

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import ProcessingStepUsedTagsEntity


class ProcessingStepUsedTagsHco(Hco[{ProcessingStepUsedTagsEntity}]):
    tags: List[str] | None = Property()

    self_link: 'ProcessingStepUsedTagsLink'

    @classmethod
    def from_entity(cls, entity: ProcessingStepUsedTagsEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["ProcessingStepUsedTags"])

        instance.self_link = ProcessingStepUsedTagsLink.from_entity(instance._client, instance._entity, Relations.SELF)

        return instance


class ProcessingStepUsedTagsLink(LinkHco):
    def navigate(self) -> ProcessingStepUsedTagsHco:
        return ProcessingStepUsedTagsHco.from_entity(self._navigate_internal(ProcessingStepUsedTagsEntity), self._client)

