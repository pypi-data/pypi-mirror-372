import logging
import re
import socket
from pathlib import Path
from typing import Optional

import requests
import yaml
from dism_core import Template
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType

from ...config import Config
from .runtimes.runtime import runtime_factory


logger = logging.getLogger(__name__)


class InferenceServiceLocalApi:
    MINIMUM_KSERVE_MAJOR = 0
    MINIMUM_KSERVE_MINOR = 10

    def __init__(
        self, isvc_name: str, container_runtime: Optional[str] = None, http_port: Optional[int] = None
    ) -> None:
        # Decide container runtime class
        self.ContainerRuntime = runtime_factory(container_runtime)
        self.http_port = http_port

        # Check build path
        self.build_path = Path(Config.build_path)
        if self.build_path.is_dir() is False:
            raise ValueError(f"Build path {self.build_path} do not exists or is not a directory.")

        # Load the built template
        template = Template.from_yaml_file(self.build_path / Config.template_name)
        if isvc_name not in template.Resources:
            raise ValueError(f"Inference Service {isvc_name} not found in built template.")

        # Select the InferenceService resource
        self.isvc = template.Resources[isvc_name]
        if self.isvc.SuperType != ResourceType.INFERENCE_SERVICE:
            raise NotImplementedError("Invoke only supports InferenceService resources.")

        # Define the serving runtime depending on the InferenceService properties
        # If the image is specified, use it; otherwise, fetch the KServe resources.
        if self.isvc.Properties.Image is not None:
            self.servingruntime = self.build_servingruntime_from_image()
        else:
            self.servingruntime = self.build_servingruntime_from_kserve(Config.kserve_tag)

        # Cwd
        self.cwd = Path.cwd()

        # Do not allow starting from inside the build path
        if self.build_path.resolve() in self.cwd.resolve().parents:
            raise ValueError(
                f'Build path "{self.build_path}" is already part of the current working directory "{self.cwd}".'
            )

    @staticmethod
    def parse_kserve_tag(kserve_tag: str):
        """
        Parses a kserve_tag like "v10.0.0", "v8.0.0", or "v9.0.0.dev1" into (major, minor, patch).

        Args:
            kserve_tag (str): The kserve tag string.

        Returns:
            tuple: A tuple (major, minor, patch) where patch can include additional identifiers like "dev1".
        """
        match = re.match(r"v(\d+)\.(\d+)\.(\d+)(.*)?", kserve_tag)
        if not match:
            raise ValueError(f"Invalid kserve_tag format: {kserve_tag}")

        major, minor, patch, extra = match.groups()
        patch = patch + extra if extra else patch
        return int(major), int(minor), patch

    @staticmethod
    def is_port_available(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) != 0

    def fetch_kserve_resources(self, kserve_tag: str) -> dict:
        response = requests.get(
            f"https://raw.githubusercontent.com/kserve/kserve/refs/tags/{kserve_tag}/charts/kserve-resources/values.yaml",
            timeout=180,
        )
        response.raise_for_status()
        return yaml.safe_load(response.text)

    def build_servingruntime_from_image(self) -> dict:
        image, tag = self.isvc.Properties.Image.split(":")
        if not tag:
            tag = "latest"
            logger.warning(
                "Image tag not specified for InferenceService %s. Defaulting to 'latest'.", self.isvc.Properties.Name
            )
        return {"image": image, "tag": tag}

    def build_servingruntime_from_kserve(self, kserve_tag: str) -> dict:
        kserve_major, kserve_minor, _ = self.parse_kserve_tag(kserve_tag)
        if (kserve_major, kserve_minor) < (self.MINIMUM_KSERVE_MAJOR, self.MINIMUM_KSERVE_MINOR):
            raise NotImplementedError(
                f"KServe major versions lesser than ({self.MINIMUM_KSERVE_MAJOR}, {self.MINIMUM_KSERVE_MINOR}) are not supported."
            )

        servingruntime = self.fetch_kserve_resources(kserve_tag)["kserve"]["servingruntime"]
        if self.isvc.ServingFrameworkType == ServingFrameworkType.TRITONSERVER and self.isvc.ModelType in (
            ModelType.TENSORFLOW_SAVEDMODEL,
            ModelType.TORCHSCRIPT,
            ModelType.ONNX,
        ):
            return servingruntime["tritonserver"]
        elif self.isvc.ServingFrameworkType == ServingFrameworkType.ML_SERVER and self.isvc.ModelType in (
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.SKLEARN,
        ):
            return servingruntime["mlserver"]
        else:
            raise NotImplementedError(f"Resource {self.isvc.Type.value} is not supported")

    def run_mlserver(self, image: str, tag: str, http_port: int):
        args = {
            "image": f"{image}:{tag}",
            "command": ["mlserver", "start", f"/mnt/{self.isvc.Properties.Name}"],
            "ports": {"8080/tcp": http_port},
            "volumes": {
                str(self.cwd / self.build_path / self.isvc.Properties.CodeUri): {
                    "bind": f"/mnt/{self.isvc.Properties.Name}",
                    "mode": "Z",
                    "readonly": True,
                }
            },
            "detach": True,
            "remove": True,
        }

        # Before starting, check if the port is available
        if not self.is_port_available(args.get("ports").get("8080/tcp")):
            raise RuntimeError("Port 8080 is already in use. Please free it before starting the container.")

        container = self.ContainerRuntime(args)
        container.run()

    def run_tritonserver(self, image: str, tag: str, http_port: int) -> None:
        # For a simple test, we don't need to expose
        # the GRPCInferenceService at port 8001
        # and the Metrics Service at port 8002
        # If we do, we also need to allow the user to specify different ports,
        # since there might be a port collision on his evironment
        args = {
            "image": f"{image}:{tag}",
            "command": ["tritonserver", "--model-repository=/models/model-repository"],
            "ports": {"8000/tcp": http_port},
            "volumes": {
                str(self.cwd / self.build_path / self.isvc.Properties.ModelRepositoryUri): {
                    "bind": "/models/model-repository",
                    "mode": "Z",
                    "readonly": True,
                }
            },
            "detach": True,
            "remove": True,
        }

        # Before starting, check if the ports are available
        for port in args.get("ports").values():
            if not self.is_port_available(port):
                raise RuntimeError(f"Port {port} is already in use. Please free it before starting the container.")

        container = self.ContainerRuntime(args)
        container.run()

    def start(self):
        if self.isvc.ServingFrameworkType == ServingFrameworkType.TRITONSERVER and self.isvc.ModelType in (
            ModelType.TENSORFLOW_SAVEDMODEL,
            ModelType.TORCHSCRIPT,
            ModelType.ONNX,
        ):
            logger.info(
                "Starting Inference Service %s using Triton Inference Server (image: %s:%s)...",
                self.isvc.Properties.Name,
                self.servingruntime["image"],
                self.servingruntime["tag"],
            )
            http_port = self.http_port or 8000
            self.run_tritonserver(self.servingruntime["image"], self.servingruntime["tag"], http_port)
        elif self.isvc.ServingFrameworkType == ServingFrameworkType.ML_SERVER and self.isvc.ModelType in (
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.SKLEARN,
        ):
            logger.info(
                "Starting Inference Service %s using MLServer (image: %s:%s)...",
                self.isvc.Properties.Name,
                self.servingruntime["image"],
                self.servingruntime["tag"],
            )
            http_port = self.http_port or 8080
            self.run_mlserver(self.servingruntime["image"], self.servingruntime["tag"], http_port)
        else:
            raise NotImplementedError(f"Resource {self.isvc.Type.value} is not supported")
