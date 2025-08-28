from typing import TypeVar, Self

import httpx
from httpx import URL

from pinexq_client.core import Entity, Action, execute_action, raise_exception_on_error, ClientException
from pinexq_client.core.hco.hco_base import ClientContainer
from pinexq_client.core.hco.unavailable import UnavailableAction, HypermediaAvailability

TEntity = TypeVar('TEntity', bound=Entity)
THcoEntity = TypeVar('THcoEntity', bound=Entity)


class ActionHco(ClientContainer, HypermediaAvailability):
    _client: httpx.Client
    _action: Action

    @classmethod
    def from_action_optional(cls, client: httpx.Client, action: Action | None) -> Self | UnavailableAction:
        if action is None:
            return UnavailableAction()

        if action.has_parameters():
            raise ClientException(f"Error while mapping action: expected action no parameters but got some")

        instance = cls(client)
        instance._action = action
        return instance

    @classmethod
    def from_entity_optional(cls, client: httpx.Client, entity: Entity, name: str) -> Self | UnavailableAction:
        if entity is None:
            return UnavailableAction()

        action = entity.find_first_action_with_name(name)
        return cls.from_action_optional(client, action)

    @classmethod
    def from_action(cls, client: httpx.Client, action: Action) -> Self:
        action = cls.from_action_optional(client, action)
        if isinstance(action, UnavailableAction):
            raise ClientException(
                f"Error while mapping mandatory action: does not exist")
        return action

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, name: str) -> Self:
        result = cls.from_entity_optional(client, entity, name)
        if isinstance(result, UnavailableAction):
            raise ClientException(
                f"Error while mapping mandatory action {name}: does not exist")
        return result

    @staticmethod
    def is_available() -> bool:
        return True

    def _execute_internal(self) -> None | URL:
        response = execute_action(self._client, self._action)
        raise_exception_on_error(f"Error while executing action, unexpected response", response)
        return response

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self._action.name}'>"
