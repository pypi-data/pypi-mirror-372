"""Classes."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field, model_validator

from .base_api import BaseOneRosterModel


class Demographics(BaseOneRosterModel["Demographics"]):
    """Classes."""

    birth_date: str | None = Field(None, alias="birthDate")

    _resource_path: ClassVar[str] = "demographic"

    @model_validator(mode="after")
    def get_date_from_datetime(cls, values):
        birth_iso = datetime.fromisoformat(values.birth_date)
        birth_date = birth_iso.date()
        values.birth_date = birth_date.isoformat()

        return values
