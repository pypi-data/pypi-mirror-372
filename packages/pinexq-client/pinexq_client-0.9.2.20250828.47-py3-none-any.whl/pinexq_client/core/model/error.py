from typing import Any

from pydantic import BaseModel


class ProblemDetails(BaseModel):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None
    errors: Any = None

    def __str__(self):
        message = [f"  {key}: {value}" for key, value in self.model_dump().items() if value]
        return str.join("\n", message)
