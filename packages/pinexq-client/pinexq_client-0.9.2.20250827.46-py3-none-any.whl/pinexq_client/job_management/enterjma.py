from typing import TypeVar, Type

import httpx

import warnings

from pinexq_client.core import Entity
from pinexq_client.core.enterapi import enter_api
from pinexq_client.core.hco.hco_base import Hco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.model.sirenentities import EntryPointEntity
import pinexq_client.job_management

THco = TypeVar("THco", bound=Hco)


def _version_match_major_minor(ver1: list[int], ver2: list[int]) -> bool:
    return all([v1 == v2 for v1, v2 in zip(ver1[:2], ver2[:2])])


def enter_jma(
    client: httpx.Client,
    entrypoint_hco_type: Type[THco] = EntryPointHco,
    entrypoint_entity_type: Type[Entity] = EntryPointEntity,
    entrypoint: str = "api/EntryPoint",
) -> EntryPointHco:
    entry_point_hco = enter_api(client, entrypoint_hco_type, entrypoint_entity_type, entrypoint)

    info = entry_point_hco.info_link.navigate()

    # Check for matching protocol versions
    client_version = pinexq_client.job_management.__jma_version__
    jma_version = [int(i) for i in str.split(info.api_version, '.')]
    if not _version_match_major_minor(jma_version, client_version):
        warnings.warn(
            f"Version mismatch between 'pinexq_client' (v{'.'.join(map(str ,client_version))}) "
            f"and 'JobManagementAPI' (v{'.'.join(map(str, jma_version))})! "
        )

    return entry_point_hco
