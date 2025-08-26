from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from dismcli.lib.package.packager import ApplicationPackager


@pytest.fixture
def mock_config():
    with patch("dismcli.lib.package.packager.Config") as mock_config:
        mock_config.package_path = "/tmp/package_path"
        mock_config.build_path = "/tmp/build_path"
        mock_config.template_name = "template.yaml"
        yield mock_config


@pytest.fixture
def mock_dials_minio():
    with patch("dismcli.lib.package.packager.DialsMinioClient") as mock_client:
        # Access the instance that would be returned when DialsMinioClient() is called
        mock_instance = mock_client.return_value
        # Configure the method to return a string
        mock_instance.presigned_put_object.return_value = "https://test-bucket/path=1/to=2/key=object"
        yield mock_instance


@pytest.fixture
def mock_template():
    with patch("dismcli.lib.package.packager.Template") as mock_template:
        mock_instance = MagicMock()
        mock_instance.Resources = {}
        mock_template.from_yaml_file.return_value = mock_instance
        yield mock_template


@pytest.fixture
def mock_creds():
    return MagicMock()


@patch("pathlib.Path.exists", side_effect=[True])
@patch("shutil.rmtree")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
def test_init_creates_directories(
    mock_is_dir, mock_mkdir, mock_rmtree, mock_exists, mock_config, mock_dials_minio, mock_template, mock_creds
):
    ApplicationPackager(mock_creds)
    mock_rmtree.assert_called_once_with(Path(mock_config.package_path))
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=False)


@patch("pathlib.Path.exists", side_effect=[False])
@patch("shutil.rmtree")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
def test_init_package_path_not_exists(
    mock_is_dir, mock_mkdir, mock_rmtree, mock_exists, mock_config, mock_dials_minio, mock_template, mock_creds
):
    ApplicationPackager(mock_creds)
    mock_rmtree.assert_not_called()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=False)


@patch("pathlib.Path.exists", side_effect=[False])
@patch("shutil.rmtree")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[False])
def test_init_build_path_not_dir(
    mock_is_dir, mock_mkdir, mock_rmtree, mock_exists, mock_config, mock_dials_minio, mock_template, mock_creds
):
    with pytest.raises(ValueError, match=f"Build path {mock_config.build_path} do not exists or is not a directory."):
        ApplicationPackager(mock_creds)
    mock_rmtree.assert_not_called()


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
@patch("zipfile.ZipFile")
@patch("requests.put")
def test_package_inference_service(
    mock_put, mock_zipfile, mock_is_dir, mock_mkdir, mock_config, mock_dials_minio, mock_template, mock_creds
):
    packager = ApplicationPackager(mock_creds)
    resource = MagicMock()
    resource.ServingFrameworkType = ServingFrameworkType.TRITONSERVER
    resource.ModelType = ModelType.TENSORFLOW_SAVEDMODEL
    resource.Properties.ModelRepositoryUri = "model_repo"

    mock_put.return_value.raise_for_status = MagicMock()
    mock_files_to_zip = [
        Path(mock_config.build_path) / resource.Properties.ModelRepositoryUri / "fingerprint.pb",
        Path(mock_config.build_path) / resource.Properties.ModelRepositoryUri / "variables/0001",
        Path(mock_config.build_path) / resource.Properties.ModelRepositoryUri / "variables/0002",
    ]
    with (
        patch("pathlib.Path.rglob", return_value=mock_files_to_zip),
        patch("builtins.open", return_data="zipdata-rb"),
        patch("pathlib.Path.is_file", side_effect=[True, True, True]),
    ):
        packager.package_inference_service(resource)

    mock_zipfile.assert_called_once()
    mock_put.assert_called_once()


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
def test_package_resource_inference_service(mock_mkdir, mock_config, mock_dials_minio, mock_template, mock_creds):
    packager = ApplicationPackager(mock_creds)
    resource = MagicMock()
    resource.SuperType = ResourceType.INFERENCE_SERVICE

    with patch.object(packager, "package_inference_service") as mock_package_inference_service:
        packager.package_resource(resource)
        mock_package_inference_service.assert_called_once_with(resource)


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
def test_package_resource_unsupported_type(mock_mkdir, mock_config, mock_dials_minio, mock_template, mock_creds):
    packager = ApplicationPackager(mock_creds)
    resource = MagicMock()

    class NotImplementedResourceType(Enum):
        OTHER_SERVICE = "OtherService"

    resource.SuperType = NotImplementedResourceType.OTHER_SERVICE

    with pytest.raises(NotImplementedError, match="Resource super type OtherService is not supported"):
        packager.package_resource(resource)


@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_dir", side_effect=[True])
def test_call(mock_is_dir, mock_mkdir, mock_config, mock_dials_minio, mock_template, mock_creds):
    packager = ApplicationPackager(mock_creds, ignore_duplicates=False)

    # Create a mock resource
    resource = MagicMock()
    resource.Type = "InferenceService::Tritonserver::Torchscript"
    resource.Properties.Name = "my_model"
    packager.template.Resources = {"test_resource": resource}

    # Mock self.dials
    mock_model = MagicMock()
    mock_model.revision = 1
    mock_response = MagicMock()
    mock_response.results = [mock_model]  # simulate a model already exists
    packager.dials = MagicMock()
    packager.dials.ml_models_index.list_all.return_value = mock_response

    with (
        patch.object(packager, "package_resource") as mock_package_resource,
        patch.object(packager.template, "to_yaml") as mock_to_yaml,
        patch("builtins.input", return_value="y"),  # simulate user input
    ):
        packager()
        mock_package_resource.assert_called_once_with(resource)
        mock_to_yaml.assert_called_once_with(Path(mock_config.package_path) / mock_config.template_name)
        packager.dials.ml_models_index.list_all.assert_called_once()
