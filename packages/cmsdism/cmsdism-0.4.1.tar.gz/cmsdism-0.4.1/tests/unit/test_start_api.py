from enum import Enum
from unittest.mock import MagicMock, create_autospec, patch

import pytest
from dism_core.properties.isvc.base import InferenceServiceProperties
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from dismcli.lib.start_api.start_api import InferenceServiceLocalApi


@pytest.fixture
def mock_config():
    with patch("dismcli.lib.start_api.start_api.Config") as mock_config:
        mock_config.build_path = "/tmp/build_path"
        mock_config.template_name = "template.yaml"
        mock_config.kserve_tag = "v0.14.0"
        yield mock_config


@pytest.fixture
def mock_unsupported_config():
    with patch("dismcli.lib.start_api.start_api.Config") as mock_config:
        mock_config.build_path = "/tmp/build_path"
        mock_config.template_name = "template.yaml"
        mock_config.kserve_tag = "v0.8.0"
        yield mock_config


@pytest.fixture
def mock_template():
    with patch("dismcli.lib.start_api.start_api.Template") as mock_template:
        mock_instance = MagicMock()
        resource = create_autospec(InferenceServiceResource, instance=True)
        resource.SuperType = ResourceType.INFERENCE_SERVICE
        resource.ServingFrameworkType = ServingFrameworkType.TRITONSERVER
        resource.ModelType = ModelType.ONNX
        resource.Workspace = "test_workspace"
        resource.Properties = create_autospec(InferenceServiceProperties, instance=True)
        resource.Properties.Image = None
        mock_instance.Resources = {"GenericModel": resource}
        mock_template.from_yaml_file.return_value = mock_instance
        yield mock_template


@pytest.fixture
def mock_container():
    with patch("dismcli.lib.start_api.start_api.runtime_factory") as mock_container:
        yield mock_container


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_init_valid_isvc(mock_is_dir, mock_template, mock_config):
    api = InferenceServiceLocalApi("GenericModel")
    assert api.isvc.SuperType == ResourceType.INFERENCE_SERVICE


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_init_unsupported_kserve_tag(mock_is_dir, mock_template, mock_unsupported_config):
    with pytest.raises(NotImplementedError, match="KServe major versions lesser than .* are not supported."):
        InferenceServiceLocalApi("GenericModel")


@patch("pathlib.Path.is_dir", side_effect=[False])
def test_init_invalid_build_path(mock_config):
    with pytest.raises(ValueError, match="Build path .* do not exists or is not a directory."):
        InferenceServiceLocalApi("GenericModel")


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_init_invalid_isvc_name(mock_is_dir, mock_template, mock_config):
    mock_template.from_yaml_file.return_value.Resources = {}
    with pytest.raises(ValueError, match="Inference Service .* not found in built template."):
        InferenceServiceLocalApi("GenericModel")


def test_is_port_available():
    assert InferenceServiceLocalApi.is_port_available(9999) is True


@patch("pathlib.Path.is_dir", side_effect=[True])
@patch("dismcli.lib.start_api.start_api.requests.get")
def test_fetch_kserve_resources(mock_get, mock_is_dir, mock_template, mock_config):
    mock_response = MagicMock()
    mock_response.text = "kserve:\n  servingruntime:\n    tritonserver:\n      image: triton\n      tag: latest"
    mock_get.return_value = mock_response
    mock_response.raise_for_status = MagicMock()

    api = InferenceServiceLocalApi("GenericModel")
    resources = api.fetch_kserve_resources("v0.14.0")
    assert "kserve" in resources
    assert "servingruntime" in resources["kserve"]


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_run_mlserver(mock_config, mock_template, mock_container):
    mock_template.from_yaml_file.return_value.Resources = {
        **mock_template.from_yaml_file.return_value.Resources,
        "MLServerModel": MagicMock(
            SuperType=ResourceType.INFERENCE_SERVICE,
            ServingFrameworkType=ServingFrameworkType.ML_SERVER,
            ModelType=ModelType.XGBOOST,
            Properties=MagicMock(Name="test_model", CodeUri="/tmp/code_uri", Image=None),
        ),
    }
    api = InferenceServiceLocalApi("MLServerModel")
    with patch.object(api, "is_port_available", return_value=True):
        api.run_mlserver("mlserver_image", "latest", None)
        mock_container.assert_called_once()


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_start_mlserver(mock_config, mock_template):
    mock_template.from_yaml_file.return_value.Resources = {
        "MLServerModel": MagicMock(
            SuperType=ResourceType.INFERENCE_SERVICE,
            ServingFrameworkType=ServingFrameworkType.ML_SERVER,
            ModelType=ModelType.XGBOOST,
            Properties=MagicMock(CodeUri="/tmp/code_uri", Image=None),
        )
    }
    api = InferenceServiceLocalApi("MLServerModel")
    with patch.object(api, "run_mlserver") as mock_run_mlserver:
        api.start()
        mock_run_mlserver.assert_called_once()


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_run_tritonserver(mock_config, mock_template, mock_container):
    mock_template.from_yaml_file.return_value.Resources = {
        **mock_template.from_yaml_file.return_value.Resources,
        "TritonserverModel": MagicMock(
            SuperType=ResourceType.INFERENCE_SERVICE,
            ServingFrameworkType=ServingFrameworkType.TRITONSERVER,
            ModelType=ModelType.TENSORFLOW_SAVEDMODEL,
            Properties=MagicMock(ModelRepositoryUri="/tmp/model-repository", Image=None),
        ),
    }
    api = InferenceServiceLocalApi("TritonserverModel")
    with patch.object(api, "is_port_available", return_value=True):
        api.run_tritonserver("triton_image", "latest", None)
        mock_container.assert_called_once()


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_start_tritonserver(mock_config, mock_template):
    mock_template.from_yaml_file.return_value.Resources = {
        "TritonserverModel": MagicMock(
            SuperType=ResourceType.INFERENCE_SERVICE,
            ServingFrameworkType=ServingFrameworkType.TRITONSERVER,
            ModelType=ModelType.TENSORFLOW_SAVEDMODEL,
            Properties=MagicMock(ModelRepositoryUri="/tmp/model-repository", Image=None),
        )
    }
    api = InferenceServiceLocalApi("TritonserverModel")
    with patch.object(api, "run_tritonserver") as mock_run_tritonserver:
        api.start()
        mock_run_tritonserver.assert_called_once()


@patch("pathlib.Path.is_dir", side_effect=[True])
def test_start_unsupported_resource(mock_config, mock_template):
    class NotImplementedServingFrameworkType(Enum):
        XGBOOSTSERVER = "XGBoostServer"

    mock_template.from_yaml_file.return_value.Resources = {
        "XGBoostServerModel": MagicMock(
            SuperType=ResourceType.INFERENCE_SERVICE,
            ServingFrameworkType=NotImplementedServingFrameworkType.XGBOOSTSERVER,
            ModelType=ModelType.XGBOOST,
            Type=MagicMock(value="InferenceService::MLServer::XGBoostServer"),
            Properties=MagicMock(Image=None),
        )
    }
    with pytest.raises(
        NotImplementedError, match="Resource InferenceService::MLServer::XGBoostServer is not supported"
    ):
        _ = InferenceServiceLocalApi("XGBoostServerModel")
