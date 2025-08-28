from typing import Self, Type

import httpx
from httpx import URL
from httpx import Response

from pinexq_client.core import Link, Entity, navigate, ensure_siren_response, ClientException, raise_exception_on_error, \
    ApiException
from pinexq_client.core.hco.hco_base import ClientContainer, TEntity
from pinexq_client.core.hco.unavailable import UnavailableLink, HypermediaAvailability
from pinexq_client.core.model.error import ProblemDetails


class LinkHco(ClientContainer, HypermediaAvailability):

    _client: httpx.Client
    _link: Link

    @classmethod
    def from_link_optional(cls, client: httpx.Client, link: Link | None) -> Self | UnavailableLink:
        if link is None:
            return UnavailableLink()

        instance = cls(client)
        instance._link = link
        return instance

    @classmethod
    def from_entity_optional(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self | UnavailableLink:
        if entity is None:
            return UnavailableLink()

        link = entity.find_first_link_with_relation(link_relation)
        return cls.from_link_optional(client, link)

    @classmethod
    def from_link(cls, client: httpx.Client, link: Link) -> Self:
        result = cls.from_link_optional(client, link)
        if isinstance(result, UnavailableLink):
            raise ClientException(f"Error while mapping mandatory link: link is None")

        return result

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self:
        result = cls.from_entity_optional(client, entity, link_relation)
        if isinstance(result, UnavailableLink):
            raise ClientException(
                f"Error while mapping mandatory link: entity contains no link with relation {link_relation}")

        return result

    @staticmethod
    def is_available() -> bool:
        return True

    """Checks if the resource can be retrieved (no 404) """
    def exists(self) -> bool:
        response = navigate(self._client, self._link)
        match response:
            case Response() as r:
                if r.status_code == 404:
                    # resource is not found
                    return False
                elif r.status_code == 200:
                    # resource found
                    return True
                elif r.status_code >= 400:
                    raise_exception_on_error("Expected a resource or none, got error", r)
                else:
                    raise ApiException(f"Unexpected status code in response: {r.status_code}")

            case ProblemDetails() as p:
                if p.status == 404:
                    # resource is not found
                    return False
                elif p.status == 200:
                    # resource found
                    return True
                elif p.status >= 400:
                    raise_exception_on_error("Expected a resource or none, got error", p)
                else:
                    raise ApiException(f"Unexpected status code in response: {p.status_code}")
            case _:
                # got entity
                return True

    def _navigate_internal(self, parse_type: Type[TEntity] = Entity) -> TEntity:
        response = navigate(self._client, self._link, parse_type)
        return ensure_siren_response(response)

    def get_url(self) -> URL:
        return URL(self._link.href)

    def __eq__(self, other):
        """Compares the link url to determine if the link is pointing to the same resource."""
        if isinstance(other, LinkHco):
            return self.get_url() == other.get_url()
        else:
            return NotImplemented

    def __repr__(self):
        rel_names = ', '.join((f"'{r}'" for r in self._link.rel))
        return f"<{self.__class__.__name__}: {rel_names}>"
