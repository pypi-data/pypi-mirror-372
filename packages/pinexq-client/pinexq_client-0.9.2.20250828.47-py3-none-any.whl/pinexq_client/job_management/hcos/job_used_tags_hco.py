from typing import List, Self

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import JobUsedTagsEntity


class JobUsedTagsHco(Hco[JobUsedTagsEntity]):
    tags: List[str] | None = Property()

    self_link: 'JobUsedTagsLink'

    @classmethod
    def from_entity(cls, entity: JobUsedTagsEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["JobUsedTags"])

        instance.self_link = JobUsedTagsLink.from_entity(instance._client, instance._entity, Relations.SELF)

        return instance


class JobUsedTagsLink(LinkHco):
    def navigate(self) -> JobUsedTagsHco:
        return JobUsedTagsHco.from_entity(self._navigate_internal(JobUsedTagsEntity), self._client)

