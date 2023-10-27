from src.handlers.bugcrowd_api import BugCrowdAPI
from src.env import RESPONSES
import logging
import json

logger = logging.getLogger(__name__)

class BugCrowdSubmission:
    def __init__(self, submission_id, classification, reasoning):
        """
        Initializes a BugCrowdSubmission object.

        :param submission_id: ID of the submission.
        :param classification: Classification information for the submission.
        :param reasoning: Reasoning information for the submission.
        """
        self.submission_id = submission_id
        self.classification = classification
        self.reasoning = reasoning

    def _prepare_assign_data(self, user_id):
        """
        Prepares data to assign a user to the submission.

        :param user_id: ID of the user to be assigned.
        :return: Dictionary containing the required data.
        """
        return {
            'data': {
                'type': 'submission',
                'relationships': {
                    'assignee': {
                        'data': {
                            'id': user_id,
                            'type': 'identity'
                        }
                    }
                }
            }
        }

    def _handle_assign_response(self, response, user_id):
        """
        Handles the response after assigning a user to the submission.

        :param response: Response object from the assignment operation.
        :param user_id: ID of the user assigned.
        """
        if response.status_code == 200:
            logger.info(f"Submission {self.submission_id} assigned to user {user_id}.")
        else:
            logger.error(f"Unable to assign submission {self.submission_id} to user {user_id}. Status code: {response.status_code}")

    async def assign_to_user(self, user_id):
        """
        Assigns a user to the submission.

        :param user_id: ID of the user to be assigned.
        """
        data = self._prepare_assign_data(user_id)
        response = await BugCrowdAPI.patch_submission(self.submission_id, data)
        self._handle_assign_response(response, user_id)

    async def is_submission_new(self):
        """
        Checks if the submission is new.

        :return: True if the submission is new, False otherwise.
        """
        submission_data = await BugCrowdAPI.fetch_submission(self.submission_id)
        submission_state = submission_data['data']['attributes']['state']
        return submission_state.lower() == 'new'

    async def close_submission(self):
        """
        Closes the submission on BugCrowd.
        """
        logger.info(f"Closing submission {self.submission_id} on BugCrowd.")
        data = {
            'data': {
                'type': 'submission',
                'attributes': {
                    'state': 'not_applicable'
                }
            }
        }
        response = await BugCrowdAPI.patch_submission(self.submission_id, data)
        if response.status_code != 200:
            raise Exception(f"Failed to close submission {self.submission_id}. Status code: {response.status_code}, Content: {response.content}")

    def _prepare_comment_data(self, comment_body, visibility_scope='everyone'):
        """
        Prepares data to create a comment.

        :param comment_body: Text of the comment.
        :param visibility_scope: Visibility scope of the comment. Default is 'everyone'.
        :return: Dictionary containing the required data.
        """
        return {
            "data": {
                "type": "comment",
                "attributes": {
                    "body": comment_body,
                    "visibility_scope": visibility_scope
                },
                "relationships": {
                    "submission": {
                        "data": {
                            "id": self.submission_id,
                            "type": "submission"
                        }
                    }
                }
            }
        }

    def _handle_comment_response_error(self, response):
        """
        Handles the error response for a comment creation request.

        :param response: Response object from the comment creation operation.
        """
        try:
            error_message = response.json()["errors"][0]["detail"]
        except (json.JSONDecodeError, KeyError, IndexError):
            error_message = "An error occurred, but the response is not a valid JSON object."
        logger.error("Error: " + error_message)

    async def create_comment(self, comment_body, visibility_scope='everyone'):
        """
        Creates a comment for the submission on BugCrowd.

        :param comment_body: Text of the comment.
        :param visibility_scope: Visibility scope of the comment. Default is 'everyone'.
        """
        logger.info(f"Creating comment for submission {self.submission_id} on BugCrowd.")
        comment_data = self._prepare_comment_data(comment_body, visibility_scope)
        response = await BugCrowdAPI.create_comment(comment_data)
        if response.status_code in [400, 404, 409]:
            self._handle_comment_response_error(response)
        elif response.status_code != 201:
            logger.error("An unexpected error occurred.")

    def generate_comment_text(self):
        """
        Generates the text for a comment based on the classification.

        :return: Generated comment text or None if the classification is not found.
        """
        try:
            specific_classification_name = self.classification.name
            specific_classification_text = RESPONSES[specific_classification_name]
            comment_text = f"Hello!\n\n{specific_classification_text}"
            return comment_text
        except KeyError:
            logger.error(f"Response for classification {self.classification.name} not found.")
            return None
