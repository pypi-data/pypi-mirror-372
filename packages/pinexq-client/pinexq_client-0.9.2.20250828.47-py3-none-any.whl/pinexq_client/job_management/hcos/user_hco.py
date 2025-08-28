from typing import Self
from uuid import UUID

import httpx

from pinexq_client.core.hco.hco_base import Hco, Property
from pinexq_client.core.hco.link_hco import LinkHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model.sirenentities import UserEntity


class UserLink(LinkHco):
    def navigate(self) -> "UserHco":
        return UserHco.from_entity(self._navigate_internal(UserEntity), self._client)


class UserHco(Hco[UserEntity]):
    user_id: UUID = Property()
    user_grants: list[str] = Property()

    self_link: UserLink

    @classmethod
    def from_entity(cls, entity: UserEntity, client: httpx.Client) -> Self:
        instance = cls(client, entity)

        Hco.check_classes(instance._entity.class_, ["User"])

        instance.self_link = UserLink.from_entity(
            instance._client, instance._entity, Relations.SELF
        )

        return instance

    def _extract_current_user(self):
        self.current_user = self._entity.find_all_entities_with_relation(
            Relations.CURRENT_USER, UserEntity)
