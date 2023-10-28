from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, Text, func
from sqlalchemy.orm import declarative_base

from bugbounty_gpt.env import VALID_CATEGORIES

Base = declarative_base()


def _sanitize_category_name(category_name):
    """
    Sanitizes the category name by replacing spaces with underscores and converting to uppercase.

    :param category_name: The category name to be sanitized.
    :return: Sanitized category name.
    """
    return category_name.replace(" ", "_").upper()


def _create_enum_members(categories):
    """
    Creates enum members from the given categories.

    :param categories: List of category names.
    :return: Dictionary with sanitized category names as keys and original category names as values.
    """
    return {_sanitize_category_name(category): category for category in categories}


ReportCategory = Enum("ReportCategory", _create_enum_members(VALID_CATEGORIES))


class SubmissionState(Enum):
    NEW = 1
    UPDATED_OUT_OF_BAND = 2
    UPDATED = 3


class Submission(Base):
    """
    Defines the Submission database table.

    Attributes:
        submission_id: Unique ID of the submission.
        user_id: ID of the user who created the submission.
        reasoning: Reasoning text for the submission.
        classification: Classification of the report using the ReportCategory enum.
        submission_state: State of the submission using the SubmissionState enum.
        created_at: Timestamp of submission creation.
        updated_at: Timestamp of the last update to the submission.
    """

    __tablename__ = "submission"

    submission_id = Column(String(100), primary_key=True)
    user_id = Column(String(100))
    reasoning = Column(Text)
    classification = Column(SqlEnum(ReportCategory))
    submission_state = Column(SqlEnum(SubmissionState))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
