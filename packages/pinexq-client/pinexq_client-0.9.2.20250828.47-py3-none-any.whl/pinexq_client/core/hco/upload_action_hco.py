from io import IOBase
from typing import Iterable, AsyncIterable, Any, Self

import httpx
from httpx import URL
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pinexq_client.core import upload_file, upload_binary, upload_json, MediaTypes, Action, Entity, \
    SirenClasses, ClientException
from pinexq_client.core.hco.action_with_parameters_hco import ActionWithParametersHco
from pinexq_client.core.hco.unavailable import UnavailableAction


class UploadParameters(BaseModel):
    # arbitrary_types_allowed
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    filename: str
    mediatype: str = MediaTypes.OCTET_STREAM

    file: IOBase | None = None
    binary: str | bytes | Iterable[bytes] | AsyncIterable[bytes] | None = None
    json_: Any | None = Field(None, alias='json')

    @model_validator(mode='after')
    def check_only_one_input_method(self) -> Self:
        list_of_vars = [self.file, self.binary, self.json_]
        initialized_vars_count = [v is not None for v in list_of_vars].count(True)

        if initialized_vars_count == 0:
            raise ValueError(f'Please provide a upload content: file, json, binary')
        if initialized_vars_count > 1:
            raise ValueError(f'Please provide only one upload content: file, json, binary')

        return self


class UploadAction(ActionWithParametersHco[UploadParameters]):
    accept: str | None = None
    max_filesize_bytes: int | None = None
    allow_multiple: bool | None = None

    @classmethod
    def from_action_optional(cls, client: httpx.Client, action: Action | None) -> Self | None:
        instance = super(UploadAction, cls).from_action_optional(client, action)

        if not isinstance(instance, UnavailableAction):
            cls.validate_file_upload_field(instance)
            cls.assign_upload_constraints(instance)
        return instance

    @classmethod
    def from_entity_optional(cls, client: httpx.Client, entity: Entity, name: str) -> Self | None:
        instance = super(UploadAction, cls).from_entity_optional(client, entity, name)

        if not isinstance(instance, UnavailableAction):
            cls.validate_file_upload_field(instance)
            cls.assign_upload_constraints(instance)
        return instance

    @classmethod
    def from_action(cls, client: httpx.Client, action: Action) -> Self:
        instance = super(UploadAction, cls).from_action(client, action)
        cls.validate_file_upload_field(instance)
        cls.assign_upload_constraints(instance)
        return instance

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, name: str) -> Self:
        instance = super(UploadAction, cls).from_entity(client, entity, name)
        cls.validate_file_upload_field(instance)
        cls.assign_upload_constraints(instance)
        return instance

    def assign_upload_constraints(self):
        upload_fields = self._action.fields[0]

        self.accept = upload_fields.accept
        self.max_filesize_bytes = upload_fields.maxFileSizeBytes
        self.allow_multiple = upload_fields.allowMultiple

    def validate_file_upload_field(self):
        action = self._action
        if SirenClasses.FileUploadAction not in action.class_:
            raise ClientException(
                f"Upload action does not have expected class: {str(SirenClasses.FileUploadAction)}. Got: {action.class_}")

        if action.type != MediaTypes.MULTIPART_FORM_DATA.value:
            raise ClientException(
                f"Upload action does not have expected type: {str(MediaTypes.MULTIPART_FORM_DATA)}. Got: {action.type}")

        upload_fields = self._action.fields[0]

        if upload_fields.type != "file":
            raise ClientException(
                f"Upload action does not have expected field type: 'file'. Got: {upload_fields.type}")

    def _upload(self, parameters: UploadParameters) -> URL:

        result = None
        if parameters.file is not None:
            result = upload_file(self._client, self._action, parameters.file, parameters.filename, parameters.mediatype)

        elif parameters.binary is not None:
            result = upload_binary(self._client, self._action, parameters.binary, parameters.filename,
                                   parameters.mediatype)

        elif parameters.json_ is not None:
            result = upload_json(self._client, self._action, parameters.json_, parameters.filename)
        else:
            raise ClientException("Did not execute upload, none selected")

        if not isinstance(result, URL):
            raise ClientException("Upload did not respond with location")
        return result
