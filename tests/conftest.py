import pytest


@pytest.fixture
def mock_async_sleep(mocker):
    return mocker.patch("asyncio.sleep")
