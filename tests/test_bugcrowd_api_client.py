from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import pytest, asyncio

from bugbounty_gpt.env import BUGCROWD_API_KEY, API_BASE_URL
from bugbounty_gpt.handlers.bugcrowd_api import BugCrowdAPI

def test_get_headers():
    headers = BugCrowdAPI._get_headers()
    assert headers['Accept'] == 'application/vnd.bugcrowd+json'
    assert headers['Authorization'] == f'Token {BUGCROWD_API_KEY}'

@pytest.mark.asyncio
async def test_fetch_page():
    url = f"{API_BASE_URL}/submissions"
    params = {"param": "value"}
    page_limit = 5
    page_offset = 0

    mock_response = AsyncMock(status_code=200)
    mock_response.json = MagicMock(return_value={"data": ["submission1", "submission2"]})  # Use MagicMock for the synchronous json method

    with patch.object(httpx.AsyncClient, 'get', return_value=mock_response) as mock_get:
        submissions = await BugCrowdAPI._fetch_page(url, params, page_limit, page_offset) # await the async function
        assert submissions == ["submission1", "submission2"]  # No await here

@pytest.mark.asyncio
async def test_fetch_submissions():
    params = {"param": "value"}
    with patch("bugbounty_gpt.handlers.bugcrowd_api.BugCrowdAPI._fetch_page", new_callable=AsyncMock) as mock_fetch_page:
        mock_fetch_page.side_effect = [["submission1", "submission2"], []]
        submissions = await BugCrowdAPI.fetch_submissions(params)
        assert submissions == ["submission1", "submission2"]

@pytest.mark.asyncio
async def test_fetch_submission():
    submission_id = "test_id"

    mock_response = AsyncMock(status_code=200)
    mock_response.json = MagicMock(return_value={"data": "submission_data"})  # Use MagicMock for the synchronous json method

    with patch.object(httpx.AsyncClient, 'get', return_value=mock_response) as mock_get:
        submission = await BugCrowdAPI.fetch_submission(submission_id)
        assert submission == {"data": "submission_data"}  # No await here

@pytest.mark.asyncio
async def test_create_comment():
    comment_data = {"data": "comment_data"}
    mock_response = AsyncMock()
    mock_response.status_code = 201

    with patch.object(httpx.AsyncClient, 'post', return_value=mock_response) as mock_post:
        response = await BugCrowdAPI.create_comment(comment_data)
        assert response.status_code == 201

    mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_patch_submission():
    submission_id = "test_id"
    data = {"data": "patch_data"}

    mock_json = AsyncMock(return_value={"data": "patched_submission_data"})
    mock_response = AsyncMock(status_code=200, json=mock_json)

    with patch.object(httpx.AsyncClient, 'patch', return_value=mock_response) as mock_patch:
        response = await BugCrowdAPI.patch_submission(submission_id, data)
        assert await response.json() == {"data": "patched_submission_data"}

    mock_patch.assert_called_once()
