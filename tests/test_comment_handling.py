import logging
from unittest.mock import AsyncMock, patch

import pytest

from bugbounty_gpt.handlers.bugcrowd_api import BugCrowdAPI
from bugbounty_gpt.handlers.submission_handler import BugCrowdSubmission


@pytest.mark.asyncio
async def test_create_comment_success():
    submission = BugCrowdSubmission("submission_id", None, None)
    comment_body = "Test comment"

    with patch.object(BugCrowdAPI, "create_comment", new_callable=AsyncMock) as mock_create_comment:
        await submission.create_comment(comment_body)
        mock_create_comment.assert_called_once()


@pytest.mark.asyncio
async def test_create_comment_error_handling(caplog):
    submission = BugCrowdSubmission("submission_id", None, None)
    comment_body = "Test comment"

    for error_code in [400, 404, 409]:
        mock_response = type(
            "Response",
            (object,),
            {
                "status_code": error_code,
                "json": lambda: {"errors": [{"detail": "error message"}]},
            },
        )

        with patch.object(
            BugCrowdAPI,
            "create_comment",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with caplog.at_level(logging.ERROR):  # Capture ERROR-level logs
                await submission.create_comment(comment_body)

                # Check if the expected error message was logged
                assert "Error: error message" in caplog.text

            caplog.clear()  # Clear the captured logs for the next iteration
