from typing import Self

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.hcos.user_hco import UserHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import InfoEntity, UserEntity


class InfoLink(LinkHco):
    def navigate(self) -> "InfoHco":
        return InfoHco.from_entity(self._navigate_internal(InfoEntity), self._client)


class InfoHco(Hco[InfoEntity]):
    api_version: str = Property()
    build_version: str = Property()
    current_user: UserHco
    organization_id: str = Property()
    used_storage_in_bytes: int = Property()

    self_link: InfoLink

    @classmethod
    def from_entity(cls, entity: InfoEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["Info"])

        instance.self_link = InfoLink.from_entity(
            instance._client, instance._entity, Relations.SELF
        )

        instance._extract_current_user()

        return instance

    def _extract_current_user(self):
        user_entity = self._entity.find_first_entity_with_relation(
            Relations.CURRENT_USER, UserEntity)
        self.current_user = UserHco.from_entity(user_entity, self._client)
