from unittest.mock import patch

import pytest

from bugbounty_gpt.env import DEFAULT_CATEGORY, OPENAI_MODEL, OPENAI_PROMPT
from bugbounty_gpt.handlers.openai_handler import OpenAIHandler


def test_classifications_sanitization():
    assert OpenAIHandler._classifications_sanitization(" Test Category ") == "TEST_CATEGORY"


def test_build_request_data():
    submission_content = "Sample content"
    expected_data = {
        "model": OPENAI_MODEL,
        "temperature": 0,
        "max_tokens": 512,
        "messages": [
            {"role": "system", "content": OPENAI_PROMPT},
            {"role": "user", "content": submission_content},
        ],
    }
    assert OpenAIHandler._build_request_data(submission_content) == expected_data


def test_handle_response_error():
    error = Exception("Sample Error")
    with patch("bugbounty_gpt.handlers.openai_handler.logger.error") as mock_error:
        result_category, result_message = OpenAIHandler._handle_response_error(error)
        mock_error.assert_called_once_with("An error occurred during the OpenAI request: Sample Error")
        assert result_category == DEFAULT_CATEGORY
        assert result_message == "An error occurred during classification. Please check application logs."


def test_handle_response_success():
    response = type(
        "Response",
        (object,),
        {
            "choices": [
                type(
                    "Choice",
                    (object,),
                    {
                        "message": type(
                            "Message",
                            (object,),
                            {"content": "Policy or Content Complaints\nExplanation"},
                        )
                    },
                )
            ]
        },
    )
    category, explanation = OpenAIHandler._handle_response(response)
    assert category == "POLICY_OR_CONTENT_COMPLAINTS"
    assert explanation == "Explanation"


def test_handle_response_unsanitized_category():
    response = type(
        "Response",
        (object,),
        {
            "choices": [
                type(
                    "Choice",
                    (object,),
                    {
                        "message": type(
                            "Message",
                            (object,),
                            {"content": "INVALID_CATEGORY\nExplanation"},
                        )
                    },
                )
            ]
        },
    )
    category, explanation = OpenAIHandler._handle_response(response)
    assert category == DEFAULT_CATEGORY
    assert explanation == "Explanation"


def test_handle_response_exception():
    response = type("Response", (object,), {"choices": []})
    with patch("bugbounty_gpt.handlers.openai_handler.OpenAIHandler._handle_response_error") as mock_handle_error:
        OpenAIHandler._handle_response(response)
        mock_handle_error.assert_called()


@pytest.mark.asyncio
async def test_classify_submission_exception():
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.side_effect = Exception("Sample Error")
        with patch("bugbounty_gpt.handlers.openai_handler.OpenAIHandler._handle_response_error") as mock_handle_error:
            await OpenAIHandler.classify_submission("Sample content")
            mock_handle_error.assert_called()


@pytest.mark.asyncio
async def test_classify_submission_success():
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = type(
            "Response",
            (object,),
            {
                "choices": [
                    type(
                        "Choice",
                        (object,),
                        {
                            "message": type(
                                "Message",
                                (object,),
                                {"content": " Policy or Content Complaints\nExplanation"},
                            )
                        },
                    )
                ]
            },
        )
        category, explanation = await OpenAIHandler.classify_submission("Sample content")
        assert category == "POLICY_OR_CONTENT_COMPLAINTS"
        assert explanation == "Explanation"
