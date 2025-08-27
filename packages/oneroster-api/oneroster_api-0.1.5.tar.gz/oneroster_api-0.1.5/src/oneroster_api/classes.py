"""Classes."""

from typing import ClassVar

from pydantic import Field, model_validator

from .base_api import BaseOneRosterModel


class Classes(BaseOneRosterModel["Classes"]):
    """Classes."""

    status: str | None
    title: str | None
    class_code: str | None = Field(None, alias="classCode")
    class_type: str | None = Field(None, alias="classType")
    location: str | None
    periods: list | None
    subjects: list | None
    course: dict | None
    terms: list | None
    grades: list | None

    _resource_path: ClassVar[str] = "class"

    @model_validator(mode="after")
    def extract_academic_session(cls, values):
        data = values.terms
        values.terms = data[0]["sourcedId"]
        return values

    @model_validator(mode="after")
    def extract_course_id(cls, values):
        data = values.course
        values.course = data["sourcedId"]
        return values

    @model_validator(mode="after")
    def extract_periods(cls, values):
        data = values.periods
        values.periods = data[0]
        return values

    @model_validator(mode="after")
    def extract_subject(cls, values):
        data = values.subjects
        values.subjects = data[0]
        return values
