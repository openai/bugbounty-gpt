import asyncio
import logging
import time
from typing import Any, Dict, Tuple

import openai

from bugbounty_gpt.env import DEFAULT_CATEGORY, OPENAI_MODEL, OPENAI_PROMPT, VALID_CATEGORIES

logger = logging.getLogger(__name__)

# A type alias for the classification response; a tuple containing the judgment category and explanation.
ClassificationResponse = Tuple[str, str]


class OpenAIHandler:
    @staticmethod
    def _classifications_sanitization(input_string: str) -> str:
        """
        Sanitizes the input string by removing spaces, converting to upper case, and replacing spaces with underscores.

        :param input_string: The input string to sanitize.
        :return: The sanitized string.
        """
        return input_string.strip().replace(" ", "_").upper()

    @staticmethod
    def _build_request_data(submission_content: str) -> Dict[str, Any]:
        """
        Builds the request data for the OpenAI API.

        :param submission_content: The content of the submission to be classified.
        :return: Dictionary containing the request data.
        """
        return {
            "model": OPENAI_MODEL,
            "temperature": 0,
            "max_tokens": 512,
            "messages": [{"role": "system", "content": OPENAI_PROMPT}, {"role": "user", "content": submission_content}],
        }

    @staticmethod
    def _handle_response_error(error: Exception) -> ClassificationResponse:
        """
        Handles errors that occurred during the OpenAI request.

        :param error: The error that occurred.
        :return: A tuple containing the default category and an error message.
        """
        logger.error(f"An error occurred during the OpenAI request: {error}")
        return DEFAULT_CATEGORY, "An error occurred during classification. Please check application logs."

    @staticmethod
    def _handle_response(response: Any) -> ClassificationResponse:
        """
        Handles the response from the OpenAI API.

        :param response: The response object from the OpenAI API.
        :return: A tuple containing the judgment category and explanation, or an error response if something goes wrong.
        """
        try:
            response_text = response.choices[0].message.content
            judgement, explanation = response_text.rsplit("\n", 1)
            sanitized_judgement = OpenAIHandler._classifications_sanitization(judgement)
            if sanitized_judgement in VALID_CATEGORIES:
                return sanitized_judgement, explanation.strip()
            else:
                return DEFAULT_CATEGORY, explanation.strip()
        except Exception as error:  # pylint: disable=broad-except
            return OpenAIHandler._handle_response_error(error)

    @staticmethod
    async def classify_submission(submission_content: str) -> ClassificationResponse:
        """
        Classifies the submission content using the OpenAI API.

        :param submission_content: The content of the submission to be classified.
        :return: A tuple containing the judgment category and explanation, or an error response if something goes wrong.
        """
        logger.info("Classifying submission's content.")
        time.sleep(5)  # Consider replacing with a more robust rate-limiting strategy
        try:
            request_data = OpenAIHandler._build_request_data(submission_content)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(**request_data))
            return OpenAIHandler._handle_response(response)
        except Exception as error:  # pylint: disable=broad-except
            return OpenAIHandler._handle_response_error(error)
