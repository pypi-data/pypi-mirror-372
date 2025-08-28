from typing import List, Self

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import WorkDataUsedTagsQueryResultEntity


class WorkDataUsedTagsQueryResultHto(Hco[WorkDataUsedTagsQueryResultEntity]):
    tags: List[str] | None = Property()

    self_link: 'WorkDataUsedTagsLink'

    @classmethod
    def from_entity(cls, entity: WorkDataUsedTagsQueryResultEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["WorkDataUsedTagsQueryResult"])

        instance.self_link = WorkDataUsedTagsLink.from_entity(instance._client, instance._entity, Relations.SELF)

        return instance


class WorkDataUsedTagsLink(LinkHco):
    def navigate(self) -> WorkDataUsedTagsQueryResultHto:
        return WorkDataUsedTagsQueryResultHto.from_entity(self._navigate_internal(WorkDataUsedTagsQueryResultEntity), self._client)

