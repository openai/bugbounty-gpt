import json
import httpx
import logging
import time
from src.env import API_BASE_URL, BUGCROWD_API_KEY

logger = logging.getLogger(__name__)

class BugCrowdAPI:
    @staticmethod
    def _get_headers(content_type='application/vnd.bugcrowd+json'):
        """
        Returns common headers for Bugcrowd API requests.

        :param content_type: Content type for the Accept header. Default is 'application/vnd.bugcrowd+json'.
        :return: Dictionary containing the required headers.
        """
        return {
            'Accept': content_type,
            'Authorization': f'Token {BUGCROWD_API_KEY}'
        }

    @staticmethod
    async def _fetch_page(url, params, page_limit, page_offset):
        """
        Fetches a page of data from the specified URL with pagination.

        :param url: URL to fetch data from.
        :param params: Parameters to include in the request.
        :param page_limit: Limit of items per page.
        :param page_offset: Offset for pagination.
        :return: List of data fetched from the page or an empty list if there is an error.
        """
        pagination_params = {
            'page[limit]': page_limit,
            'page[offset]': page_offset,
        }
        complete_params = {**params, **pagination_params}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=BugCrowdAPI._get_headers(), params=complete_params)
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Error: Unable to decode JSON. {e}")
                return []

        return data['data'] if data['data'] else []

    @staticmethod
    async def fetch_submissions(params):
        """
        Fetches all submissions from BugCrowd.

        :param params: Parameters to include in the request.
        :return: List of all submissions or None if no submissions found.
        """
        logger.info("Fetching submissions from BugCrowd.")
        url = f'{API_BASE_URL}/submissions'
        page_limit = 100
        page_offset = 0
        all_submissions = []
        delay = 2  # Delay in seconds

        while True:
            submissions = await BugCrowdAPI._fetch_page(url, params, page_limit, page_offset)
            if not submissions:
                break

            all_submissions.extend(submissions)
            page_offset += page_limit

            time.sleep(delay)  # Add a delay between API calls

        return all_submissions if all_submissions else None

    @staticmethod
    async def fetch_submission(submission_id):
        """
        Fetches a specific submission from BugCrowd.

        :param submission_id: ID of the submission to fetch.
        :return: Submission data as a dictionary or None if an error occurred.
        """
        logger.info(f"Fetching submission {submission_id} from BugCrowd.")
        url = f'{API_BASE_URL}/submissions/{submission_id}'

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=BugCrowdAPI._get_headers())
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch submission {submission_id}. Status code: {response.status_code}")
                return None

    @staticmethod
    async def create_comment(comment_data):
        """
        Creates a comment using the provided data.

        :param comment_data: Data for the comment.
        :return: Response object from the comment creation operation.
        """
        url = f'{API_BASE_URL}/comments'
        headers = BugCrowdAPI._get_headers('application/json')

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=comment_data)
            if response.status_code == 201:
                logger.info("Comment created successfully.")
            else:
                logger.error(f"Failed to create comment. Status code: {response.status_code}")
            return response

    @staticmethod
    async def patch_submission(submission_id, data):
        """
        Patches a specific submission on BugCrowd.

        :param submission_id: ID of the submission to patch.
        :param data: Data to be patched.
        :return: Response object from the patch operation or None if an error occurred.
        """
        logger.info(f"Patching submission {submission_id} on BugCrowd.")
        url = f'{API_BASE_URL}/submissions/{submission_id}'
        headers = BugCrowdAPI._get_headers()
        headers['Content-Type'] = 'application/vnd.bugcrowd.v4+json'

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, data=json.dumps(data))

            if response.status_code != 200:
                logger.error(f"Failed to patch submission {submission_id}. Status code: {response.status_code}")
                return None

        return response
