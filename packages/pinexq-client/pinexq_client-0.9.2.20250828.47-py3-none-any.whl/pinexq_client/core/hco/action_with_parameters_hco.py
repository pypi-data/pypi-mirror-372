from typing import TypeVar, Type, Self, Generic

import httpx
from httpx import URL
from pydantic import BaseModel

from pinexq_client.core import Entity, Action, execute_action, raise_exception_on_error, ClientException
from pinexq_client.core.hco.hco_base import ClientContainer
from pinexq_client.core.hco.unavailable import UnavailableAction, HypermediaAvailability

TParameters = TypeVar('TParameters', bound=BaseModel)


class ActionWithParametersHco(ClientContainer, Generic[TParameters], HypermediaAvailability):
    _client: httpx.Client
    _action: Action

    @classmethod
    def from_action_optional(cls, client: httpx.Client, action: Action | None) -> Self | UnavailableAction:
        if action is None:
            return UnavailableAction()

        if not action.has_parameters():
            raise ClientException(
                f"Error while mapping action: expected action with parameters but got none")

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
                f"Error while mapping mandatory action: action does not exist")
        return action

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, name: str) -> Self:
        result = cls.from_entity_optional(client, entity, name)
        if isinstance(result, UnavailableAction):
            raise ClientException(
                f"Error while mapping mandatory action {name}: action does not exist")
        return result

    @staticmethod
    def is_available() -> bool:
        return True

    def _execute_internal(self, parameters: BaseModel) -> None | URL:
        if parameters is None:
            raise ClientException(f"Error while executing action: action requires parameters")

        response = execute_action(self._client, self._action, parameters)
        raise_exception_on_error(f"Error while executing action, unexpected response", response)
        return response

    def _execute(self, parameters: TParameters):
        result = self._execute_internal(parameters)
        if result is not None:
            raise ClientException("Action did respond with unexpected URL")
        return

    def _execute_returns_url(self, parameters: TParameters) -> URL:
        result = self._execute_internal(parameters)
        if result is None:
            raise ClientException("Action did not respond with URL")
        return result

    def _get_default_parameters(self, parameter_type: Type[TParameters],
                                default_if_none: TParameters) -> TParameters:
        return self._action.get_default_parameters(parameter_type, default_if_none)

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self._action.name}'>"
