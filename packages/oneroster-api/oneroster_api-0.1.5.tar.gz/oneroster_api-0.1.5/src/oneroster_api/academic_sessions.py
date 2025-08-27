"""Classes."""

from typing import ClassVar

from pydantic import Field

from .base_api import BaseOneRosterModel


class AcademicSessions(BaseOneRosterModel["AcademicSessions"]):
    """Classes."""

    title: str | None
    start_date: str | None = Field(None, alias="startDate")
    end_date: str | None = Field(None, alias="endDate")

    _resource_path: ClassVar[str] = "academicSession"
