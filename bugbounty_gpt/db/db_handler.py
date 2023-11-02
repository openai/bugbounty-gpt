import logging
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bugbounty_gpt.db.models import ReportCategory, Submission, SubmissionState

logger = logging.getLogger(__name__)


async def find_submission_by_id(session: AsyncSession, submission_id: str) -> Optional[Submission]:
    """
    Fetches a submission from the database by its ID.

    :param session: Database session object.
    :param submission_id: ID of the submission to be fetched.
    :return: Submission object if found, None otherwise.
    """
    logger.info(f"Fetching submission {submission_id} from database.")
    stmt = select(Submission).filter(Submission.submission_id == submission_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def insert_submission(session: AsyncSession, submission_data: Dict[str, Any]) -> None:
    """
    Inserts a new submission into the database if it does not exist.

    :param session: Database session object.
    :param submission_data: Dictionary containing the submission data.
    """
    submission_id = submission_data["submission_id"]
    logger.info(f"Checking if submission {submission_id} already exists.")
    existing_submission = await find_submission_by_id(session, submission_id)

    if existing_submission:
        logger.info(f"Submission {submission_id} already exists, skipping insert.")
        return

    logger.info(f"Inserting submission {submission_id}.")
    submission = Submission(**submission_data)
    session.add(submission)
    await session.commit()


async def update_submission_state(session: AsyncSession, submission_id: str, new_state: SubmissionState) -> bool:
    """
    Updates the state of a submission in the database.

    :param session: Database session object.
    :param submission_id: ID of the submission to be updated.
    :param new_state: New state to be assigned to the submission.
    :return: True if the update was successful, False otherwise.
    """
    logger.info(f"Updating submission {submission_id}.")
    submission = await find_submission_by_id(session, submission_id)
    if not submission:
        return False

    submission.submission_state = new_state
    await session.commit()
    return True


async def fetch_submission_by_state_and_classification(
    session: AsyncSession,
    states: List[SubmissionState],
    classifications: List[ReportCategory],
) -> Sequence[Submission]:
    """
    Fetches submissions that meet certain state and classification criteria.

    :param session: Database session object.
    :param states: List of states to filter the submissions.
    :param classifications: List of classifications to filter the submissions.
    :return: List of submissions that meet the criteria.
    """
    logger.info("Fetching submissions meeting states & classification criteria.")
    stmt = select(Submission).filter(
        Submission.submission_state.in_(states),
        Submission.classification.in_(classifications),
    )
    result = await session.execute(stmt)
    return result.scalars().all()
