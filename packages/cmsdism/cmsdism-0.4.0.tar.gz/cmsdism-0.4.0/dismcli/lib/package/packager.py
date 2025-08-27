import logging
import shutil
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests
from cmsdials import Dials
from cmsdials.auth.bearer import Credentials as BearerCredentials
from cmsdials.auth.secret_key import Credentials as SecretKeyCredentials
from cmsdials.filters import MLModelsIndexFilters
from dism_core import Template
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from ...config import Config
from .minio_uploader import DialsMinioClient


LOGGER = logging.getLogger(__name__)


class ApplicationPackager:
    def __init__(self, creds: Union[BearerCredentials, SecretKeyCredentials], ignore_duplicates: bool = False) -> None:
        self.package_path = Path(Config.package_path)
        if self.package_path.exists():
            shutil.rmtree(self.package_path)
        self.package_path.mkdir(parents=True, exist_ok=False)

        self.build_path = Path(Config.build_path)
        if self.build_path.is_dir() is False:
            raise ValueError(f"Build path {self.build_path} do not exists or is not a directory.")

        self.template = Template.from_yaml_file(self.build_path / Config.template_name)
        self.dials_minio = DialsMinioClient(creds, base_url=creds.client.base_url)
        self.dials = Dials(creds, base_url=creds.client.base_url)
        self.ignore_duplicates = ignore_duplicates

    @staticmethod
    def get_s3_location_from_presigned(url: str):
        parsed = urlparse(url)
        path_parts = parsed.path.lstrip("/").split("/", 1)

        if len(path_parts) != 2:
            raise ValueError("URL path does not contain bucket and key")

        bucket = path_parts[0]
        key = unquote(path_parts[1])  # decode %3D, spaces, etc.

        return bucket, key

    def package_inference_service(self, resource: InferenceServiceResource) -> None:
        fname = str(uuid4()).replace("-", "") + ".zip"
        isvc_zip_path = self.package_path / fname

        # Get target path based on each framework and model type
        if resource.ServingFrameworkType == ServingFrameworkType.TRITONSERVER and resource.ModelType in (
            ModelType.TENSORFLOW_SAVEDMODEL,
            ModelType.TORCHSCRIPT,
            ModelType.ONNX,
        ):
            target_path = self.build_path / resource.Properties.ModelRepositoryUri
        elif resource.ServingFrameworkType == ServingFrameworkType.ML_SERVER and resource.ModelType in (
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.SKLEARN,
        ):
            target_path = self.build_path / resource.Properties.CodeUri
        else:
            raise NotImplementedError(f"Resource {resource.Type.value} is not supported")

        # Zip all files in target path and store in package path
        with zipfile.ZipFile(isvc_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(target_path)
                    zipf.write(file_path, arcname)

        # Request S3 pre-signed URL
        presigned_url = self.dials_minio.presigned_put_object(resource.Workspace, fname)

        # PUT zip
        with open(isvc_zip_path, "rb") as f:
            response = requests.put(presigned_url, data=f, timeout=180)
        response.raise_for_status()

        # Extract bucket and key from the presigned URL
        bucket, key = self.get_s3_location_from_presigned(presigned_url)
        s3_uri = f"s3://{bucket}/{key}"

        # Update template
        if resource.ServingFrameworkType == ServingFrameworkType.TRITONSERVER and resource.ModelType in (
            ModelType.TENSORFLOW_SAVEDMODEL,
            ModelType.TORCHSCRIPT,
            ModelType.ONNX,
        ):
            resource.Properties.ModelRepositoryUri = s3_uri
        elif resource.ServingFrameworkType == ServingFrameworkType.ML_SERVER and resource.ModelType in (
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.SKLEARN,
        ):
            resource.Properties.CodeUri = s3_uri
        else:
            raise NotImplementedError(f"Resource {resource.Type.value} is not supported")

    def package_resource(self, resource: InferenceServiceResource) -> None:
        if resource.SuperType == ResourceType.INFERENCE_SERVICE:
            self.package_inference_service(resource)
        else:
            raise NotImplementedError(f"Resource super type {resource.SuperType.value} is not supported")

    def __call__(self):
        for name, resource in self.template.Resources.items():
            LOGGER.info("Packaging resource (%s, %s)", name, resource.Type)

            # Warn the user if a model with the same name already exists in DIALS
            response = self.dials.ml_models_index.list_all(MLModelsIndexFilters(name=resource.Properties.Name))
            if len(response.results) > 0:
                LOGGER.info(
                    "A model with the same name (%s) is already registered in DIALS, its latest revision is %s.",
                    resource.Properties.Name,
                    response.results[-1].revision,
                )
                if self.ignore_duplicates:
                    LOGGER.info("Ignoring existence of model with the same name, continuing with packaging.")
                else:
                    user_input = input(f"Do you want to continue packaging the resource {name}? (y/n): ")
                    if user_input.lower() != "y":
                        quit()

            self.package_resource(resource)

        self.template.to_yaml(self.package_path / Config.template_name)
