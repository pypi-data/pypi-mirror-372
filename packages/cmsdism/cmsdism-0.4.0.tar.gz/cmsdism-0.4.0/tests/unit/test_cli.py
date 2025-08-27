from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from dismcli.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("dismcli.cli.commands.start_api.InferenceServiceLocalApi")
def test_start_api_command(mock_inference_service, runner):
    mock_instance = MagicMock()
    mock_inference_service.return_value = mock_instance

    result = runner.invoke(cli, ["start-api", "--resource", "test-resource"])

    assert result.exit_code == 0
    mock_inference_service.assert_called_once_with("test-resource", None, None)
    mock_instance.start.assert_called_once()


@patch("dismcli.cli.commands.build.get_credentials")
@patch("dismcli.cli.commands.build.ApplicationBuilder")
def test_build_command(mock_builder, mock_get_credentials, runner):
    mock_instance = MagicMock()
    mock_builder.return_value = mock_instance
    mock_get_credentials.return_value = "mock-credentials"

    result = runner.invoke(cli, ["build", "--filename", "test-template", "--dials_base_url", "http://test-url"])

    assert result.exit_code == 0
    mock_get_credentials.assert_called_once_with("http://test-url")
    mock_builder.assert_called_once_with("test-template", "mock-credentials")
    mock_instance.assert_called_once()


@patch("dismcli.cli.commands.package.get_credentials")
@patch("dismcli.cli.commands.package.ApplicationPackager")
def test_package_command(mock_packager, mock_get_credentials, runner):
    mock_instance = MagicMock()
    mock_packager.return_value = mock_instance
    mock_get_credentials.return_value = "mock-credentials"

    result = runner.invoke(cli, ["package", "--dials_base_url", "http://test-url"])

    assert result.exit_code == 0
    mock_get_credentials.assert_called_once_with("http://test-url")
    mock_packager.assert_called_once_with("mock-credentials", ignore_duplicates=False)
    mock_instance.assert_called_once()
