"""Classes."""

from typing import ClassVar

from pydantic import Field

from .base_api import BaseOneRosterModel


class Courses(BaseOneRosterModel["Courses"]):
    """Classes."""

    course_code: str | None = Field(None, alias="courseCode")
    status: str | None
    school_year: dict | None = Field(None, alias="schoolYear")
    title: str | None
    grades: list | None
    subjects: list | None

    _resource_path: ClassVar[str] = "course"
