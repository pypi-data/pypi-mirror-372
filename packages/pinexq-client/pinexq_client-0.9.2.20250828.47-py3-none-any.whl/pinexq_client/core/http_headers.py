from enum import StrEnum


class Headers(StrEnum):
    API_KEY = "x-api-key"
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"
    LOCATION_HEADER = "Location"

