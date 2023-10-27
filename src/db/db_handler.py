from src.db.models import Submission
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def _find_submission_by_id(session, submission_id):
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

async def insert_submission(session, submission_data):
    """
    Inserts a new submission into the database if it does not exist.

    :param session: Database session object.
    :param submission_data: Dictionary containing the submission data.
    """
    submission_id = submission_data['submission_id']
    logger.info(f"Checking if submission {submission_id} already exists.")
    existing_submission = await _find_submission_by_id(session, submission_id)

    if existing_submission:
        logger.info(f"Submission {submission_id} already exists, skipping insert.")
    else:
        logger.info(f"Inserting submission {submission_id}.")
        async with session:
            submission = Submission(**submission_data)
            session.add(submission)
            await session.commit()

async def update_submission_state(session, submission_id, new_state):
    """
    Updates the state of a submission in the database.

    :param session: Database session object.
    :param submission_id: ID of the submission to be updated.
    :param new_state: New state to be assigned to the submission.
    :return: True if the update was successful, False otherwise.
    """
    logger.info(f"Updating submission {submission_id}.")
    async with session:
        submission = await _find_submission_by_id(session, submission_id)
        if submission:
            submission.submission_state = new_state
            await session.commit()
            return True
        else:
            return False

async def fetch_submission_by_state_and_classification(session, states, classifications):
    """
    Fetches submissions that meet certain state and classification criteria.

    :param session: Database session object.
    :param states: List of states to filter the submissions.
    :param classifications: List of classifications to filter the submissions.
    :return: List of submissions that meet the criteria.
    """
    logger.info("Fetching submissions meeting states & classification criteria.")
    async with session:
        stmt = select(Submission).filter(
            Submission.submission_state.in_(states),
            Submission.classification.in_(classifications)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

async def fetch_submission_by_id(session, submission_id):
    """
    Fetches a submission from the database by its ID.

    :param session: Database session object.
    :param submission_id: ID of the submission to be fetched.
    :return: Submission object if found, None otherwise.
    """
    logger.info(f"Fetching submission {submission_id} from database.")
    async with session:
        return session.query(Submission).filter(Submission.submission_id == submission_id).first()
