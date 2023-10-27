import logging
import asyncio

from src.db import db_handler
from src.db.models import SubmissionState
from src.handlers.openai_handler import OpenAIHandler
from src.handlers.submission_handler import BugCrowdSubmission
from src.handlers.bugcrowd_api import BugCrowdAPI
from src.env import USER_ID, FILTER_PROGRAM, RESPONSE_CATEGORIES, SQLALCHEMY_URL

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Configuration is valid.")
logger.info("Initializing database connection.")

engine = create_async_engine(SQLALCHEMY_URL, echo=False)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SEEN_SUBMISSIONS = []

async def process_new_submissions():
    """
    Fetch and process new submissions that are not duplicates and store them in the database.
    """
    params = {
        'filter[program]': FILTER_PROGRAM,
        'filter[state]': 'new',
        'filter[duplicate]': 'false'
    }

    async with SessionLocal() as session:
        if (submissions := await BugCrowdAPI.fetch_submissions(params)) is not None:
            for submission in submissions:
                # Submission processing
                submission_id = submission['id']
                if submission_id in SEEN_SUBMISSIONS:
                    continue

                user_id = submission['relationships']['researcher']['data']['id']
                submission_content = submission['attributes']['description']
                classification, reasoning = await OpenAIHandler.classify_submission(submission_content)
                submission_data = {
                    'submission_id': submission_id,
                    'user_id': user_id,
                    'classification': classification,
                    'submission_state': SubmissionState.NEW,
                    'reasoning': reasoning
                }
                SEEN_SUBMISSIONS.append(submission_id)
                await db_handler.insert_submission(session, submission_data)

async def process_in_scope_submissions():
    """
    Process submissions that are in scope by generating comments, assigning users, closing submissions,
    and updating their state in the database.
    """
    async with SessionLocal() as session:
        states = [SubmissionState.NEW]
        classifications = RESPONSE_CATEGORIES # Using the RESPONSE_CATEGORIES from config
        in_scope_submissions = await db_handler.fetch_submission_by_state_and_classification(session, states, classifications)

        for submission_data in in_scope_submissions:
            submission = BugCrowdSubmission(submission_data.submission_id, submission_data.classification, submission_data.reasoning)
            user_id = USER_ID # From config

            if await submission.is_submission_new():
                comment_body = submission.generate_comment_text()

                if comment_body:
                    await submission.create_comment(comment_body)
                    await submission.close_submission()
                    await db_handler.update_submission_state(session, submission.submission_id, SubmissionState.UPDATED)
            else:
                await db_handler.update_submission_state(session, submission.submission_id, SubmissionState.UPDATED_OUT_OF_BAND)

async def main():
    """
    Main loop that repeatedly fetches and processes new submissions and in-scope submissions.
    """
    while True:
        logger.info("Fetching and processing new submissions...")
        await process_new_submissions()

        logger.info("Processing in-scope submissions...")
        await process_in_scope_submissions()

        minutes_waited = 1
        logger.info(f"Doing nothing for {minutes_waited} minutes....")
        await asyncio.sleep(60 * minutes_waited)

if __name__ == "__main__":
    asyncio.run(main())
