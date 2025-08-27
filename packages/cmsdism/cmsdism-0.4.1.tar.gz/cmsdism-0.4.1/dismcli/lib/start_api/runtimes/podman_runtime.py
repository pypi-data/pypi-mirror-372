import logging
import shutil
import signal
import subprocess
import sys
import time
import traceback

import podman
from podman.errors.exceptions import APIError, ImageNotFound


LOGGER = logging.getLogger(__name__)


class PodmanRuntime:
    def __init__(self, args: dict) -> None:
        if not self._is_podman_installed():
            raise Exception("Podman engine is not installed.")

        # Connect to the Podman service socket
        # Default rootless socket: unix:///run/user/$UID/podman/podman.sock
        # In LXPlus the Podman API is not started by default, so we need
        # to check if the socket exists and start it if not.
        if not self._is_podman_socket_active():
            systemctl = shutil.which("systemctl")
            if not systemctl:
                raise RuntimeError("systemctl not found in PATH")

            cmd = [systemctl, "--user", "start", "podman.socket"]
            LOGGER.info('Podman socket not active. Starting Podman service using "%s"...', " ".join(cmd))
            subprocess.check_call(cmd)  # noqa: S603

            # Wait until the service becomes active
            timeout_stop = 120
            start_time = time.time()
            while not self._is_podman_socket_active():
                LOGGER.info("Waiting for Podman service to become active...")
                if time.time() - start_time > timeout_stop:
                    raise TimeoutError("Timed out waiting for Podman service to start.")
                time.sleep(1)
            LOGGER.info("Podman socket service is active.")

        self.client = podman.PodmanClient()
        self.args = args
        self.container = None

    def _is_podman_installed(self):
        podman_path = shutil.which("podman")
        if not podman_path:
            return False

        try:
            output = (
                subprocess.check_output([podman_path, "--version"], text=True, stderr=subprocess.STDOUT).strip().lower()  # noqa: S603
            )

            if "podman version" in output.lower():
                return True
            elif "docker version" in output.lower():
                return False
            else:
                raise Exception("Unexpected output from podman --version")
        except subprocess.CalledProcessError:
            return False

    def _is_podman_socket_active(self) -> bool:
        """Check if the podman.socket service is active."""
        systemctl = shutil.which("systemctl")
        if not systemctl:
            raise RuntimeError("systemctl not found in PATH")

        result = subprocess.run(  # noqa: S603
            [systemctl, "--user", "is-active", "podman.socket"], text=True, capture_output=True
        )
        return result.stdout.strip() == "active"

    def run(self):
        LOGGER.debug("Using PodmanRuntime to start container with args: %s", str(self.args))
        try:
            image = self.args.get("image")
            if image is None:
                raise ValueError("No image specified in arguments")

            # Pull the image if it doesn't exist locally
            try:
                self.client.images.get(image)
            except ImageNotFound:
                LOGGER.info("Image not found locally. Pulling '%s'...", image)
                for event in self.client.images.pull(image, stream=True):
                    LOGGER.info("%s", event.decode("utf-8").strip())
                LOGGER.info("Image '%s' pulled successfully", image)
            except APIError:
                LOGGER.error("Podman API error: %s", traceback.format_exc())
                raise

            # Create + start the container
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
