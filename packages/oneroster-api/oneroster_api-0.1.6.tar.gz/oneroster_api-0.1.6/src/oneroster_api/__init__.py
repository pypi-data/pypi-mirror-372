"""Init."""

from .academic_sessions import AcademicSessions
from .classes import Classes
from .client import set_credentials
from .courses import Courses
from .demographics import Demographics
from .enrollments import Enrollments
from .users import Users

__all__ = [
    "AcademicSessions",
    "Classes",
    "Courses",
    "Demographics",
    "Enrollments",
    "Users",
    "set_credentials",
]


def import_oneroster_data() -> dict:
    """Uses api to import all oneroster data."""
    return {
        "users": Users.retrieve_all(),
        "academic_sessions": AcademicSessions.retrieve_all(),
        "classes": Classes.retrieve_all(),
        "demographics": Demographics.retrieve_all(),
        "courses": Courses.retrieve_all(),
        "enrollments": Enrollments.retrieve_all()
    }
    # Users.download_all(import_dir)
    # AcademicSessions.download_all(import_dir)
    # Classes.download_all(import_dir)
    # Demographics.download_all(import_dir)
    # Courses.download_all(import_dir)
    # Enrollments.download_all(import_dir)
