from unittest.mock import MagicMock, patch

import pytest
from requests import HTTPError, Response, Timeout

from calllogdb.api.api_client import APIClient


@pytest.fixture
def client():
    return APIClient(url="https://fakeapi.com", token="test_token", retries_enabled=False)


def test_get_success(client):
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "ok"}
    mock_response.text = '{"result": "ok"}'

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.get(params={"key": "value"})
        mock_get.assert_called_once_with("https://fakeapi.com", params={"key": "value"})
        assert result == {"result": "ok"}


def test_get_timeout(client):
    with patch.object(client.session, "get", side_effect=Timeout):
        result = client.get()
        assert result == {}


def test_get_http_5xx_error(client):
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)

    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get()
        assert result == {}


def test_get_http_4xx_error_raises(client):
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)

    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(HTTPError):
            client.get()


def test_context_manager(client):
    with patch.object(client.session, "close") as mock_close:
        with client as c:
            assert c is client
        mock_close.assert_called_once()
