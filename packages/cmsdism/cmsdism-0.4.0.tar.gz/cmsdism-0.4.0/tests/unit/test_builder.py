from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from cmsdials.auth.bearer import Credentials
from dism_core.properties.isvc.mlserver import (
    LightGBMProperties,
    SKLearnProperties,
    XGBoostProperties,
)
from dism_core.properties.isvc.signature import DataTypeEnum
from dism_core.properties.isvc.tritonserver import (
    ONNXProperties,
    TensorflowSavedModelProperties,
    TorchscriptProperties,
    TritonserverProperties,
)
from dism_core.properties.isvc.tritonserver.base import PlatformType
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from dismcli.lib.builder.builder import ApplicationBuilder


@pytest.fixture
def builder():
    template_fpath = "examples/template.yaml"
    dials_creds = MagicMock(spec=Credentials)
    return ApplicationBuilder(template_fpath, dials_creds)


@patch("dismcli.lib.builder.builder.Template.from_yaml_file")
@patch("dismcli.lib.builder.builder.Path.mkdir")
@patch("dismcli.lib.builder.builder.shutil.rmtree")
@patch("dismcli.lib.builder.builder.Path.exists", return_value=False)
def test_init_dir_not_exists(mock_exists, mock_rmtree, mock_mkdir, mock_template):
    template_fpath = "examples/template.yaml"
    dials_creds = MagicMock(spec=Credentials)
    mock_template.return_value = MagicMock()

    ApplicationBuilder(template_fpath, dials_creds)

    mock_template.assert_called_once_with(template_fpath)
    mock_rmtree.asset_not_called()
    mock_mkdir.assert_called_once()


@patch("dismcli.lib.builder.builder.Template.from_yaml_file")
@patch("dismcli.lib.builder.builder.Path.mkdir")
@patch("dismcli.lib.builder.builder.shutil.rmtree")
@patch("dismcli.lib.builder.builder.Path.exists", return_value=True)
def test_init_dir_exists(mock_exists, mock_rmtree, mock_mkdir, mock_template):
    template_fpath = "examples/template.yaml"
    dials_creds = MagicMock(spec=Credentials)
    mock_template.return_value = MagicMock()

    ApplicationBuilder(template_fpath, dials_creds)

    mock_template.assert_called_once_with(template_fpath)
    mock_rmtree.assert_called_once()
    mock_mkdir.assert_called_once()


def test_generate_configpbtxt(builder):
    props = MagicMock(spec=TritonserverProperties)
    props.Name = "test-model"
    props.Platform = PlatformType.TENSORFLOW_SAVEDMODEL
    props.MaxBatchSize = 8
    props.InputSignature = [MagicMock(Name="input1", DataType=DataTypeEnum.FP32, Dims=[1, 224, 224, 3])]
    props.OutputSignature = [MagicMock(Name="output1", DataType=DataTypeEnum.FP32, Dims=[1, 1000])]

    result = builder.generate_configpbtxt(props)

    assert 'name: "test-model"' in result
    assert 'platform: "tensorflow_savedmodel"' in result
    assert "max_batch_size: 8" in result
    assert 'name: "input1"' in result
    assert 'name: "output1"' in result


def test_generate_model_settings(builder):
    props = MagicMock()
    props.Name = "test-model"
    props.Handler = "app.Handler"
    props.ModelUri = Path("/path/to/model-repository")

    result = builder.generate_model_settings(props)

    assert result["name"] == "test-model"
    assert result["implementation"] == "app.Handler"
    assert result["parameters"]["uri"] == "/path/to/model-repository"
    assert result["parameters"]["version"] == "0.1.0"


@patch("dismcli.lib.builder.builder.shutil.copytree")
@patch("dismcli.lib.builder.builder.shutil.copy2")
def test_build_saved_model(mock_copy2, mock_copytree, builder):
    # Parepare mocks
    version_path = Path("/path/to/model/version")
    fingerpint_file = Path("/path/to/fingerprint.pb")
    variables_dir = Path("/path/to/variables")
    props = MagicMock()
    props.SavedModelUri.glob.return_value = [fingerpint_file, variables_dir]

    # Test function
    with patch("pathlib.Path.is_dir", side_effect=[False, True]):
        builder.build_saved_model(props, version_path)

    # Assert
    mock_copy2.assert_called_once_with(fingerpint_file, version_path / "fingerprint.pb")
    mock_copytree.assert_called_once_with(variables_dir, version_path / "variables")


@patch("dismcli.lib.builder.builder.shutil.copy2")
def test_build_model_uri(mock_copy2, builder):
    # Parepare mocks
    props = MagicMock()
    props.ModelUri = Path("/path/to/model/file1")
    isvc_build_path = Path("/path/to/build")

    # Test function
    builder.build_model_uri(props, isvc_build_path)

    # Assert
    mock_copy2.assert_called_once_with(props.ModelUri, isvc_build_path / "file1")


@patch("dismcli.lib.builder.builder.shutil.copy2")
@patch("dismcli.lib.builder.builder.shutil.copytree")
def test_build_code_uri(mock_copytree, mock_copy2, builder):
    # Prepare mocks
    file_path = Path("/path/to/code/file1")
    dir_path = Path("/path/to/code/dir1")
    isvc_build_path = Path("/path/to/build")
    props = MagicMock()
    props.CodeUri.glob.return_value = [file_path, dir_path]

    # Test function
    with patch("pathlib.Path.is_dir", side_effect=[False, True]):
        builder.build_code_uri(props, isvc_build_path)

    # Assert
    mock_copy2.assert_called_once_with(file_path, isvc_build_path / "file1")
    mock_copytree.assert_called_once_with(dir_path, isvc_build_path / "dir1")


@patch("dismcli.lib.builder.builder.shutil.rmtree")
@patch("dismcli.lib.builder.builder.Path.mkdir")
def test_create_build_path_from_existing(mock_mkdir, mock_rmtree, builder):
    # Prepare mocks
    name = "test_service"
    builder.build_path = Path("/path/to/build")

    # Test function
    with patch("pathlib.Path.exists", side_effect=[True]):
        result = builder.create_build_path(name)

    # Assert
    assert result == builder.build_path / name
    mock_rmtree.assert_called_once_with(builder.build_path / name)
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=False)


@patch("dismcli.lib.builder.builder.shutil.rmtree")
@patch("dismcli.lib.builder.builder.Path.mkdir")
def test_create_build_path_from_non_existing(mock_mkdir, mock_rmtree, builder):
    # Prepare mocks
    name = "test_service"
    builder.build_path = Path("/path/to/build")

    # Test function
    with patch("pathlib.Path.exists", side_effect=[False]):
        result = builder.create_build_path(name)

    # Assert
    assert result == builder.build_path / name
    mock_rmtree.assert_not_called()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=False)


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_saved_model")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_configpbtxt")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("builtins.open", new_callable=mock_open)
def test_build_tensorflow_savedmodel_inference_service(
    mock_file, mock_create_build_path, mock_generate_configpbtxt, mock_build_saved_model, mock_validator, builder
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.TRITONSERVER
    resource.ModelType = ModelType.TENSORFLOW_SAVEDMODEL
    resource.Properties = MagicMock(spec=TensorflowSavedModelProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.SavedModelUri = Path("/path/to/saved_model")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_saved_model.assert_called_once()
    mock_generate_configpbtxt.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_model_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_configpbtxt")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("builtins.open", new_callable=mock_open)
def test_build_torchscript_inference_service(
    mock_file, mock_create_build_path, mock_generate_configpbtxt, mock_build_model_uri, mock_validator, builder
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.TRITONSERVER
    resource.ModelType = ModelType.TORCHSCRIPT
    resource.Properties = MagicMock(spec=TorchscriptProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.ModelUri = Path("/path/to/model.pt")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_model_uri.assert_called_once()
    mock_generate_configpbtxt.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_model_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_configpbtxt")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("builtins.open", new_callable=mock_open)
def test_build_onnx_inference_service(
    mock_file, mock_create_build_path, mock_generate_configpbtxt, mock_build_model_uri, mock_validator, builder
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.TRITONSERVER
    resource.ModelType = ModelType.TORCHSCRIPT
    resource.Properties = MagicMock(spec=ONNXProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.ModelUri = Path("/path/to/model.onnx")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_model_uri.assert_called_once()
    mock_generate_configpbtxt.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_code_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_model_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_model_settings")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("dismcli.lib.builder.builder.json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_build_xgboost_inference_service(
    mock_file,
    mock_json_dump,
    mock_create_build_path,
    mock_generate_model_settings,
    mock_build_code_uri,
    mock_build_model_uri,
    mock_validator,
    builder,
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.ML_SERVER
    resource.ModelType = ModelType.XGBOOST
    resource.Properties = MagicMock(spec=XGBoostProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.CodeUri = Path("/path/to/code_uri")
    resource.Properties.ModelUri = Path("/path/to/model.ubj")
    resource.Properties.Handler = Path("app.Handler")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_json_dump.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_model_uri.assert_called_once()
    mock_build_code_uri.assert_called_once()
    mock_generate_model_settings.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_code_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_model_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_model_settings")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("dismcli.lib.builder.builder.json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_build_lightgbm_inference_service(
    mock_file,
    mock_json_dump,
    mock_create_build_path,
    mock_generate_model_settings,
    mock_build_code_uri,
    mock_build_model_uri,
    mock_validator,
    builder,
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.ML_SERVER
    resource.ModelType = ModelType.LIGHTGBM
    resource.Properties = MagicMock(spec=LightGBMProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.CodeUri = Path("/path/to/code_uri")
    resource.Properties.ModelUri = Path("/path/to/model.txt")
    resource.Properties.Handler = Path("app.Handler")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_json_dump.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_model_uri.assert_called_once()
    mock_build_code_uri.assert_called_once()
    mock_generate_model_settings.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_code_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_model_uri")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.generate_model_settings")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
@patch("dismcli.lib.builder.builder.json.dump")
@patch("builtins.open", new_callable=mock_open)
def test_build_sklearn_inference_service(
    mock_file,
    mock_json_dump,
    mock_create_build_path,
    mock_generate_model_settings,
    mock_build_code_uri,
    mock_build_model_uri,
    mock_validator,
    builder,
):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.ML_SERVER
    resource.ModelType = ModelType.SKLEARN
    resource.Properties = MagicMock(spec=SKLearnProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.CodeUri = Path("/path/to/code_uri")
    resource.Properties.ModelUri = Path("/path/to/model.joblib")
    resource.Properties.Handler = Path("app.Handler")
    resource.Properties.ModelRepositoryUri = None

    builder.build_inference_service("test_service", resource)

    mock_file.assert_called_once()
    mock_json_dump.assert_called_once()
    mock_create_build_path.assert_called_once()
    mock_validator.assert_called_once_with(resource, builder.creds)
    mock_build_model_uri.assert_called_once()
    mock_build_code_uri.assert_called_once()
    mock_generate_model_settings.assert_called_once()


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
def test_not_implemented_serving_framework(mock_create_build_path, mock_build_inference_service, builder):
    class NotImplementedServingFrameworkType(Enum):
        XGBOOST_SERVER = "xgboostserver"

    resource = MagicMock(spec=InferenceServiceResource)
    resource.Type = "InferenceService::xgboostserver::XGBoost"
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = NotImplementedServingFrameworkType.XGBOOST_SERVER
    resource.ModelType = ModelType.XGBOOST
    resource.Properties = MagicMock(spec=XGBoostProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.CodeUri = Path("/path/to/code_uri")
    resource.Properties.ModelUri = Path("/path/to/model.ubj")
    resource.Properties.Handler = Path("app.Handler")
    resource.Properties.ModelRepositoryUri = None

    with pytest.raises(NotImplementedError, match=f"Resource {resource.Type} is not supported"):
        builder.build_resource("test_service", resource)


@patch("dismcli.lib.builder.builder.InputSignatureValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.create_build_path")
def test_not_implemented_model_type(mock_create_build_path, mock_build_inference_service, builder):
    class NotImplementedModelType(Enum):
        CATBOOST = "Catboost"

    resource = MagicMock(spec=InferenceServiceResource)
    resource.Type = "InferenceService::MLServer::Catboost"
    resource.SuperType = ResourceType.INFERENCE_SERVICE
    resource.ServingFrameworkType = ServingFrameworkType.ML_SERVER
    resource.ModelType = NotImplementedModelType.CATBOOST
    resource.Properties = MagicMock(spec=XGBoostProperties)
    resource.Properties.Name = "test-model"
    resource.Properties.CodeUri = Path("/path/to/code_uri")
    resource.Properties.ModelUri = Path("/path/to/model")
    resource.Properties.Handler = Path("app.Handler")
    resource.Properties.ModelRepositoryUri = None

    with pytest.raises(NotImplementedError, match=f"Resource {resource.Type} is not supported"):
        builder.build_resource("test_service", resource)


@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_inference_service")
def test_build_resource(mock_build_inference_service, builder):
    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = ResourceType.INFERENCE_SERVICE

    builder.build_resource("test_service", resource)

    mock_build_inference_service.assert_called_once_with("test_service", resource)


@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_inference_service")
def test_not_implemented_resource(mock_build_inference_service, builder):
    class NotImplementedResourceType(Enum):
        OTHER_SERVICE = "OtherService"

    resource = MagicMock(spec=InferenceServiceResource)
    resource.SuperType = NotImplementedResourceType.OTHER_SERVICE

    with pytest.raises(NotImplementedError, match="Resource super type OtherService is not supported"):
        builder.build_resource("test_service", resource)


@patch("dismcli.lib.builder.builder.InferenceServiceValidator")
@patch("dismcli.lib.builder.builder.ApplicationBuilder.build_resource")
@patch("dismcli.lib.builder.builder.yaml.dump")
@patch("builtins.open", new_callable=mock_open)
def test_call(mock_file, mock_yaml_dump, mock_build_resource, mock_validator, builder):
    builder.template = MagicMock()
    builder.template.Resources.items.return_value = [("test_service", MagicMock())]
    builder.build_path = Path("/path/to/build")

    builder()

    mock_validator.assert_called_once_with(builder.template)
    mock_build_resource.assert_called_once()
    mock_file.assert_called_once()
    mock_yaml_dump.assert_called_once()
