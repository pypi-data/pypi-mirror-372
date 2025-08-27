import logging
import shutil
import signal
import subprocess
import sys
import traceback

import docker
from docker.errors import APIError, ImageNotFound


LOGGER = logging.getLogger(__name__)


class DockerRuntime:
    def __init__(self, args: dict) -> None:
        if not self._is_docker_installed():
            raise Exception("Docker engine is not installed.")

        self.client = docker.from_env()
        self.args = args
        self.container = None

    def _is_docker_installed(self):
        docker_path = shutil.which("docker")
        if not docker_path:
            return False

        try:
            output = (
                subprocess.check_output([docker_path, "--version"], text=True, stderr=subprocess.STDOUT).strip().lower()  # noqa: S603
            )

            if "podman version" in output.lower():
                return False
            elif "docker version" in output.lower():
                return True
            else:
                raise Exception("Unexpected output from docker --version")
        except subprocess.CalledProcessError:
            return False

    def run(self):
        LOGGER.debug("Using DockerRuntime to start container with args: %s", str(self.args))
        try:
            image = self.args.get("image")
            if image is None:
                raise ValueError("No image specified in arguments")

            # Pull the image if it doesn't exist locally
            try:
                self.client.images.get(image)
            except ImageNotFound:
                LOGGER.info("Image not found locally. Pulling '%s'...", image)
                for event in self.client.api.pull(image, stream=True, decode=True):
                    LOGGER.info("%s", event)
                LOGGER.info("Image '%s' pulled successfully", image)
            except APIError:
                LOGGER.error("Docker API error: %s", traceback.format_exc())
                raise

            # Start the container
            self.container = self.client.containers.run(**self.args)
            LOGGER.info("Container started. Press Ctrl+C to stop.")

            # Handle SIGINT (Ctrl+C) to stop and remove container
            signal.signal(signal.SIGINT, self.cleanup)

            # Stream logs in real-time
            for line in self.container.logs(stream=True, follow=True, stdout=True, stderr=True):
                sys.stdout.buffer.write(line)
                sys.stdout.flush()
        except Exception:  # noqa: BLE001
            LOGGER.error("Error starting container: %s", traceback.format_exc())
            self.cleanup()

    def cleanup(self, signum=None, frame=None):
        """Stops and removes the container on Ctrl+C"""
        if self.container:
            self.container.stop()
            # We do not need to explicitly remove the container, since we use "remove=True" when creating it
            # self.container.remove()
