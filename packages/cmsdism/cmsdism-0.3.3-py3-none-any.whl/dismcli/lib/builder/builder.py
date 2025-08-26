import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Union

import yaml
from cmsdials.auth.bearer import Credentials
from dism_core import InferenceServiceValidator, Template
from dism_core.properties.isvc.mlserver import (
    LightGBMProperties,
    MLServerProperties,
    SKLearnProperties,
    XGBoostProperties,
)
from dism_core.properties.isvc.tritonserver import (
    ONNXProperties,
    TensorflowSavedModelProperties,
    TorchscriptProperties,
    TritonserverProperties,
)
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from ...config import Config
from .input_validator import InputSignatureValidator


logger = logging.getLogger(__name__)


class ApplicationBuilder:
    def __init__(self, template_fpath: Union[str, Path], dials_creds: Credentials) -> None:
        self.creds = dials_creds
        self.template = Template.from_yaml_file(template_fpath)
        self.build_path = Path(Config.build_path)
        if self.build_path.exists():
            shutil.rmtree(self.build_path)
        self.build_path.mkdir(parents=True, exist_ok=False)

    @staticmethod
    def generate_configpbtxt(props: TritonserverProperties) -> str:
        configs_inputs = "input [\n"
        for idx, signature in enumerate(props.InputSignature):
            dims = ", ".join([str(value) for value in signature.Dims])
            configs_inputs += f'  {{\n    name: "{signature.Name}"\n    data_type: {signature.DataType.value}\n    dims: [{dims}]\n  }}'
            if idx + 1 < len(props.InputSignature):
                configs_inputs += ","
            configs_inputs += "\n"
        configs_inputs += "]"

        configs_outputs = "output [\n"
        for idx, signature in enumerate(props.OutputSignature):
            dims = ", ".join([str(value) for value in signature.Dims])
            configs_outputs += f'  {{\n    name: "{signature.Name}"\n    data_type: {signature.DataType.value}\n    dims: [{dims}]\n  }}'
            if idx + 1 < len(props.OutputSignature):
                configs_outputs += ","
            configs_outputs += "\n"
        configs_outputs += "]"

        return f"""name: "{props.Name}"
platform: "{props.Platform.value}"
max_batch_size: {props.MaxBatchSize}
{configs_inputs}
{configs_outputs}
"""

    @staticmethod
    def generate_model_settings(
        props: Union[XGBoostProperties, LightGBMProperties, SKLearnProperties],
    ) -> dict:
        return {
            "name": props.Name,
            "implementation": props.Handler,
            "parameters": {"uri": str(props.ModelUri), "version": "0.1.0"},
        }

    @staticmethod
    def build_saved_model(props: TensorflowSavedModelProperties, version_path: Path) -> None:
        for src_path in props.SavedModelUri.glob("*"):
            dst_path = version_path / src_path.parts[-1]
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    @staticmethod
    def build_model_uri(
        props: Union[ONNXProperties, TorchscriptProperties, LightGBMProperties, SKLearnProperties, XGBoostProperties],
        isvc_build_path: Path,
        new_model_filename: Optional[str] = None,
    ) -> None:
        filename = new_model_filename if new_model_filename else props.ModelUri.parts[-1]
        dst_path = isvc_build_path / filename
        shutil.copy2(props.ModelUri, dst_path)

    @staticmethod
    def build_code_uri(props: MLServerProperties, isvc_build_path: Path) -> None:
        for src_path in props.CodeUri.glob("*"):
            dst_path = isvc_build_path / src_path.parts[-1]
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

    def create_build_path(self, name: str) -> Path:
        build_path = self.build_path / name
        if build_path.exists():
            shutil.rmtree(build_path)
        build_path.mkdir(parents=True, exist_ok=False)
        return build_path

    def build_inference_service(self, name: str, resource: InferenceServiceResource) -> None:
        isvc_build_path = self.create_build_path(name)
        ivalidator = InputSignatureValidator(resource, self.creds)
        ivalidator.validate()

        if (
            resource.ServingFrameworkType == ServingFrameworkType.TRITONSERVER
            and resource.ModelType == ModelType.TENSORFLOW_SAVEDMODEL
        ):
            # Relative path to the saved model version files
            rel_version_path = Path(resource.Properties.Name) / "1" / "model.savedmodel"

            # Destination build path of the model repository model version
            version_path = isvc_build_path / rel_version_path
            version_path.mkdir(parents=True)

            # Build the files to the correct path
            self.build_saved_model(resource.Properties, version_path)
            resource.Properties.SavedModelUri = rel_version_path
            resource.Properties.ModelRepositoryUri = Path(name)

            # Generate the config pbtxt file and
            # save in the model repository path
            repo_path = isvc_build_path / Path(resource.Properties.Name)
            config_pbtxt = self.generate_configpbtxt(resource.Properties)
            with open(repo_path / Config.triton_config, "w") as f:
                f.write(config_pbtxt)
        elif resource.ServingFrameworkType == ServingFrameworkType.TRITONSERVER and resource.ModelType in (
            ModelType.TORCHSCRIPT,
            ModelType.ONNX,
        ):
            # Relative path to the saved model version files
            rel_version_path = Path(resource.Properties.Name) / "1"

            # Destination build path of the model repository model version
            version_path = isvc_build_path / rel_version_path
            version_path.mkdir(parents=True)

            # Build the files to the correct path
            if resource.ModelType == ModelType.TORCHSCRIPT:
                new_model_filename = "model.pt"
            elif resource.ModelType == ModelType.ONNX:
                new_model_filename = "model.onnx"

            self.build_model_uri(resource.Properties, version_path, new_model_filename)
            resource.Properties.ModelUri = version_path / new_model_filename
            resource.Properties.ModelRepositoryUri = Path(name)

            # Generate the config pbtxt file and
            # save in the model repository path
            repo_path = isvc_build_path / Path(resource.Properties.Name)
            config_pbtxt = self.generate_configpbtxt(resource.Properties)
            with open(repo_path / Config.triton_config, "w") as f:
                f.write(config_pbtxt)
        elif resource.ServingFrameworkType == ServingFrameworkType.ML_SERVER and resource.ModelType in (
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.SKLEARN,
        ):
            self.build_model_uri(resource.Properties, isvc_build_path)
            self.build_code_uri(resource.Properties, isvc_build_path)
            resource.Properties.CodeUri = Path(name)
            resource.Properties.ModelUri = Path(resource.Properties.ModelUri.parts[-1])

            # Generate the model settings file and
            # save in the destination build path of the model
            model_settings = self.generate_model_settings(resource.Properties)
            with open(isvc_build_path / Config.mlserver_config, "w") as f:
                json.dump(model_settings, f)
        else:
            raise NotImplementedError(f"Resource {resource.Type} is not supported")

    def build_resource(self, name: str, resource: InferenceServiceResource) -> None:
        if resource.SuperType == ResourceType.INFERENCE_SERVICE:
            self.build_inference_service(name, resource)
        else:
            raise NotImplementedError(f"Resource super type {resource.SuperType.value} is not supported")

    def __call__(self):
        isvc_validator = InferenceServiceValidator(self.template)
        isvc_validator()

        for name, resource in self.template.Resources.items():
            logger.info("Building resource (%s, %s)", name, resource.Type)
            self.build_resource(name, resource)

        with open(self.build_path / "template.yaml", "w") as f:
            yaml.dump(self.template.model_dump(mode="json"), f)
