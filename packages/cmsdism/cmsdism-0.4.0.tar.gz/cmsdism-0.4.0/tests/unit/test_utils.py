from unittest.mock import MagicMock, patch

from dismcli.config import Config
from dismcli.lib.utils import get_credentials


@patch("dismcli.lib.utils.AuthClient")
@patch("dismcli.lib.utils.Credentials")
def test_get_credentials_with_base_url(mock_credentials, mock_auth_client):
    base_url = "https://example.com"
    mock_auth_instance = MagicMock()
    mock_auth_client.return_value = mock_auth_instance
    mock_credentials.from_creds_file.return_value = "mocked_credentials"
    Config.dials_dev_cache_dir = "/mock/cache/dir"

    result = get_credentials(base_url)

    mock_auth_client.assert_called_once_with(base_url=base_url)
    mock_credentials.from_creds_file.assert_called_once_with(cache_dir="/mock/cache/dir", client=mock_auth_instance)
    assert result == "mocked_credentials"


@patch("dismcli.lib.utils.AuthClient")
@patch("dismcli.lib.utils.Credentials")
def test_get_credentials_without_base_url(mock_credentials, mock_auth_client):
    base_url = None
    mock_auth_instance = MagicMock()
    mock_auth_client.return_value = mock_auth_instance
    mock_credentials.from_creds_file.return_value = "mocked_credentials"

    result = get_credentials(base_url)

    mock_auth_client.assert_called_once_with(base_url=base_url)
    mock_credentials.from_creds_file.assert_called_once_with(cache_dir=None, client=mock_auth_instance)
    assert result == "mocked_credentials"
