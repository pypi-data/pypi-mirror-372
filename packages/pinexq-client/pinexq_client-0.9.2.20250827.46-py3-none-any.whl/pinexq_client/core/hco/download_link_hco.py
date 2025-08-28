from typing import Self

import httpx
from httpx import Response

from pinexq_client.core import Link, Entity, get_resource, ClientException
from pinexq_client.core.hco.link_hco import LinkHco


class DownloadLinkHco(LinkHco):

    @classmethod
    def from_link_optional(cls, client: httpx.Client, link: Link | None) -> Self | None:
        return super(DownloadLinkHco, cls).from_link_optional(client, link)

    @classmethod
    def from_entity_optional(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self | None:
        return super(DownloadLinkHco, cls).from_entity_optional(client, entity, link_relation)

    @classmethod
    def from_link(cls, client: httpx.Client, link: Link) -> Self:
        return super(DownloadLinkHco, cls).from_link(client, link)

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self:
        return super(DownloadLinkHco, cls).from_entity(client, entity, link_relation)

    def download(self) -> bytes:
        response: Response = get_resource(self._client, self._link.href, self._link.type)
        if not isinstance(response, Response):
            raise ClientException(
                f"Error while downloading resource: did not get response type")

        return response.content

    # TODO: download for large files
