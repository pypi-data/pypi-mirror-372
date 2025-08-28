import httpx

from typing import TypeVar, Type
from pinexq_client.core.sirenaccess import get_resource, raise_exception_on_error
from pinexq_client.core.model.sirenmodels import Entity
from pinexq_client.core.hco.hco_base import Hco

THco = TypeVar('THco', bound=Hco)


def enter_api(client: httpx.Client,
              entrypoint_hco_type: Type[THco],
              entrypoint_entity_type: Type[Entity] = Entity,
              entrypoint: str = "api/EntryPoint") -> THco:
    entry_point_response = get_resource(client=client, href=entrypoint, parse_type=entrypoint_entity_type)
    raise_exception_on_error("Error accessing the API", entry_point_response)
    return entrypoint_hco_type.from_entity(entry_point_response, client)
