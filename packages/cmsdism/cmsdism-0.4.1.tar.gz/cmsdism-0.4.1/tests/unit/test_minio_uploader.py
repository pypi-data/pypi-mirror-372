from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from dismcli.lib.package.minio_uploader import DialsMinioClient


@pytest.fixture
def mock_creds():
    creds = MagicMock()
    creds.before_request = MagicMock()
    return creds


@pytest.fixture
def dials_minio_client(mock_creds):
    return DialsMinioClient(creds=mock_creds, base_url="http://mock-api-url.com/")


def test_build_headers(dials_minio_client, mock_creds):
    # Act
    headers = dials_minio_client._build_headers()

    # Assert
    assert "Accept" in headers
    assert "Content-Type" in headers
    assert "User-Agent" in headers
    mock_creds.before_request.assert_called_once_with(headers)


@patch("dismcli.lib.package.minio_uploader.requests.post")
def test_presigned_put_object_success(mock_post, dials_minio_client):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"url": "http://mock-presigned-url.com"}
    mock_post.return_value = mock_response
    object_name = "test_object.txt"

    result = dials_minio_client.presigned_put_object("test-workspace", object_name)

    assert result == "http://mock-presigned-url.com"
    mock_post.assert_called_once_with(
        f"{dials_minio_client.api_url}minio/ml-presigned-put-object/",
        headers=dials_minio_client._build_headers(),
        json={"workspace": "test-workspace", "object_name": object_name},
        timeout=dials_minio_client.default_timeout,
    )


@patch("dismcli.lib.package.minio_uploader.requests.post")
def test_presigned_put_object_http_error(mock_post, dials_minio_client):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("HTTP Error occurred")
    mock_response.text = "Error details"
    mock_post.return_value = mock_response
    object_name = "test_object.txt"

    with pytest.raises(HTTPError):
        dials_minio_client.presigned_put_object("test-workspace", object_name)

    mock_post.assert_called_once_with(
        f"{dials_minio_client.api_url}minio/ml-presigned-put-object/",
        headers=dials_minio_client._build_headers(),
        json={"workspace": "test-workspace", "object_name": object_name},
        timeout=dials_minio_client.default_timeout,
    )
