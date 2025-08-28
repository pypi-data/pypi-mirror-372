from io import IOBase
from typing import Self, Any, Iterable, AsyncIterable

import httpx
from httpx import URL

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.upload_action_hco import UploadParameters
from pinexq_client.job_management.enterjma import enter_jma
from pinexq_client.job_management.hcos import WorkDataLink, WorkDataRootHco, WorkDataHco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import SetTagsWorkDataParameters, CopyWorkDataFromUserToOrgActionParameters


class WorkData:
    """Convenience wrapper for handling WorkDataHcos in the JobManagement-Api.
    """

    _client: httpx.Client
    _entrypoint: EntryPointHco
    _work_data_root: WorkDataRootHco
    work_data_hco: WorkDataHco | None = None # Internal hco of the wrapper. This is updated by this class. You should not take a reference to this object.

    def __init__(self, client: httpx.Client):
        """

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
        """
        self._client = client
        self._entrypoint = enter_jma(client)
        self._work_data_root = self._entrypoint.work_data_root_link.navigate()

    def create(
            self,
            *,
            filename: str,
            mediatype: str = MediaTypes.OCTET_STREAM,
            json: Any | None = None,
            file: IOBase | None = None,
            binary: str | bytes | Iterable[bytes] | AsyncIterable[bytes] | None = None
    ) -> Self:
        work_data_link = self._work_data_root.upload_action.execute(
            UploadParameters(
                filename=filename, binary=binary, json=json, file=file, mediatype=mediatype
            )
        )
        self._get_by_link(work_data_link)
        return self

    def _get_by_link(self, work_data_link: WorkDataLink):
        self.work_data_hco = work_data_link.navigate()

    @classmethod
    def from_hco(cls, work_data_hco: WorkDataHco) -> Self:
        """Initializes a `WorkData` object from an existing WorkDataHco object.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            work_data_hco: The WorkDataHco to initialize this WorkData from.

        Returns:
            The newly created work data as `WorkData` object.
        """

        work_data_instance = cls(work_data_hco._client)
        work_data_instance.work_data_hco = work_data_hco
        return work_data_instance

    @classmethod
    def from_url(cls, client: httpx.Client, work_data_url: URL) -> Self:
        """Initializes a `WorkData` object from an existing work data given by its link as URL.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            work_data_url: The URL of the work data

        Returns:
            The newly created work data as `WorkData` object
        """
        link = Link.from_url(
            work_data_url,
            [str(Relations.CREATED_RESSOURCE)],
            "Uploaded work data",
            MediaTypes.SIREN,
        )
        processing_step_instance = cls(client)
        processing_step_instance._get_by_link(WorkDataLink.from_link(client, link))
        return processing_step_instance

    def refresh(self) -> Self:
        """Updates the work data from the server

        Returns:
            This `WorkData` object, but with updated properties.
        """
        self._raise_if_no_hco()
        self.work_data_hco = self.work_data_hco.self_link.navigate()
        return self

    def set_tags(self, tags: list[str]):
        """Set tags to the processing step.

        Returns:
            This `WorkData` object"""
        self._raise_if_no_hco()
        self.work_data_hco.edit_tags_action.execute(SetTagsWorkDataParameters(
            tags=tags
        ))
        self.refresh()
        return self

    def allow_deletion(self) -> Self:
        """Allow deletion.

        Returns:
            This `WorkData` object"""
        self._raise_if_no_hco()
        self.work_data_hco.allow_deletion_action.execute()
        self.refresh()
        return self

    def disallow_deletion(self) -> Self:
        """Disallow deletion.

        Returns:
            This `WorkData` object"""
        self._raise_if_no_hco()
        self.work_data_hco.disallow_deletion_action.execute()
        self.refresh()
        return self

    def hide(self) -> Self:
        """Hide WorkData.

        Returns:
            This `WorkData` object"""
        self._raise_if_no_hco()
        self.work_data_hco.hide_action.execute()
        self.refresh()
        return self

    def delete(self) -> Self:
        """Delete WorkData.

        Returns:
            This `WorkData` object"""
        self._raise_if_no_hco()
        self.work_data_hco.delete_action.execute()
        self.work_data_hco = None
        return self

    def download(self) -> bytes:
        """Download WorkData.

        Returns:
            Downloaded WorkData in bytes
        """
        self._raise_if_no_hco()
        return self.work_data_hco.download_link.download()

    def copy_to_user(self) -> WorkDataLink:
        """Copy WorkData from organization to user.

        Returns:
            The URL of the copied WorkData
        """
        self._raise_if_no_hco()
        return self.work_data_hco.copy_org_to_user_action.execute()

    def copy_to_org(self, org_id: str) -> WorkDataLink:
        """Copy WorkData from user to organization.

        Args:
            org_id: The ID of the organization to copy the WorkData to.

        Returns:
            The URL of the copied WorkData
        """
        self._raise_if_no_hco()
        return self.work_data_hco.copy_user_to_org_action.execute(
            CopyWorkDataFromUserToOrgActionParameters(org_id=org_id)
        )

    def self_link(self) -> WorkDataLink:
        self._raise_if_no_hco()
        return self.work_data_hco.self_link

    def _raise_if_no_hco(self):
        if self.work_data_hco is None:
            raise Exception("No work data hco present. Maybe this class is used after resource deletion.")