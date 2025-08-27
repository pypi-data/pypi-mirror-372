"""Users."""

from typing import Any, ClassVar

from pydantic import Field, model_validator

from .base_api import BaseOneRosterModel


class Users(BaseOneRosterModel["Users"]):
    """User Object."""

    username: int | None
    status: str | None
    role: str | None
    enabled: bool | None = Field(None, alias="enabledUser")
    state_id: int | None  # = Field(None, alias="userIds")
    first_name: str | None = Field(None, alias="givenName")
    last_name: str | None = Field(None, alias="familyName")
    middle_name: str | None = Field(None, alias="middleName")
    preferred_first_name: str | None = Field(None, alias="preferredFirstName")
    preferred_last_name: str | None = Field(None, alias="preferredLastName")
    email: str | None
    identifier: int | None
    grades: list | None

    _resource_path: ClassVar[str] = "user"

    @model_validator(mode="before")
    def get_preferred_name(cls, values: Any) -> Any:
        # print(values["metadata"])
        if values["metadata"] is not None:
            if values["metadata"]["preferredFirstName"] is not None:
                values["preferredFirstName"] = values["metadata"]["preferredFirstName"]
            if values["metadata"]["preferredLastName"] is not None:
                values["preferredLastName"] = values["metadata"]["preferredLastName"]
        return values

    @model_validator(mode="after")
    def extract_grade(cls, values: Any) -> Any:
        """Extracts grade from list."""
        if values.role == "student":
            values.grades = values.grades[0]
        return values

    @model_validator(mode="before")
    def extract_state_id(cls, values: Any) -> Any:
        """Returns the state id from dict."""
        values["state_id"] = None
        if values["role"] == "student":
            for item in values["userIds"]:
                if item["type"] == "SSID":
                    values["state_id"] = item["identifier"]
        elif values["role"] == "teacher":
            if values["metadata"]["stateId"] is not None:
                values["state_id"] = values["metadata"]["stateId"]

        return values
