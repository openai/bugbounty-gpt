from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from src.env import SQLALCHEMY_URL
import time
import logging

logger = logging.getLogger(__name__)
logger.info("Migration auto-init script activated. To turn this off, re-build without the EPHEMERAL_DB arg.")
time.sleep(2)

SYNCHRONOUS_SQLALCHEMY_URL = SQLALCHEMY_URL.replace("+asyncpg", "")

engine = create_engine(SYNCHRONOUS_SQLALCHEMY_URL)

# Number of attempts to connect to the database
MAX_ATTEMPTS = 5
# Time (in seconds) to wait between each attempt
WAIT_TIME = 5

def check_and_init_submission_table(engine):
    """
    Checks if the 'submission' table exists, and if not, runs an alembic migration to create it.

    :param engine: The SQLAlchemy engine to use for inspecting the database and running migrations.
    """
    inspector = inspect(engine)
    if "submission" not in inspector.get_table_names():
        logger.info("Submission table not found - attempting alembic auto-generate & init.")
        alembic_cfg = Config("/usr/src/app/alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message="Auto-generated migration for 'submission' table.")
        command.upgrade(alembic_cfg, "head")

def attempt_database_connection(engine):
    """
    Attempts to connect to the database, and initializes the submission table if it does not exist.

    :param engine: The SQLAlchemy engine to use for inspecting the database and running migrations.
    """
    for attempt in range(MAX_ATTEMPTS):
        try:
            check_and_init_submission_table(engine)
            break # Exit the loop if connection is successful
        except OperationalError as e:
            logger.warning(f"Failed to connect to database (attempt {attempt + 1} of {MAX_ATTEMPTS}). Retrying in {WAIT_TIME} seconds...")
            time.sleep(WAIT_TIME)
    else:
        # This block executes if the loop completes without a 'break' statement (i.e., all attempts failed)
        logger.error("Failed to connect to database after all attempts. Exiting.")
        raise Exception("Unable to connect to database")

# Starting the connection attempts
attempt_database_connection(engine)
