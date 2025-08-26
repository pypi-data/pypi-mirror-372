import importlib
from unittest.mock import patch

import pytest

from dismcli.lib.start_api.runtimes import runtime


def test_no_runtime(monkeypatch):
    with patch("importlib.util.find_spec", return_value=None):
        # reload to re-evaluate flags with patched find_spec
        importlib.reload(runtime)

        with pytest.raises(ImportError, match="Docker/Podman SDK for Python is not installed"):
            runtime.runtime_factory()

    # restore to normal for other tests
    importlib.reload(runtime)


def test_docker_runtime_only():
    def fake_find_spec(name: str):
        if name == "docker":
            return object()  # pretend docker is available
        return None  # podman not available

    with patch("importlib.util.find_spec", side_effect=fake_find_spec):
        importlib.reload(runtime)

        # No argument -> should default to DockerRuntime
        result = runtime.runtime_factory()
        assert result is runtime.DockerRuntime

        # Explicit docker -> should also return DockerRuntime
        result = runtime.runtime_factory("docker")
        assert result is runtime.DockerRuntime

        # Explicit podman -> should raise since unavailable
        with pytest.raises(ImportError, match="Podman SDK for Python is not installed"):
            runtime.runtime_factory("podman")

    importlib.reload(runtime)


def test_podman_runtime_only():
    def fake_find_spec(name: str):
        if name == "podman":
            return object()  # pretend podman is available
        return None  # docker not available

    with patch("importlib.util.find_spec", side_effect=fake_find_spec):
        importlib.reload(runtime)

        # No argument -> should default to PodmanRuntime
        result = runtime.runtime_factory()
        assert result is runtime.PodmanRuntime

        # Explicit podman -> should also return PodmanRuntime
        result = runtime.runtime_factory("podman")
        assert result is runtime.PodmanRuntime

        # Explicit docker -> should raise since unavailable
        with pytest.raises(ImportError, match="Docker SDK for Python is not installed"):
            runtime.runtime_factory("docker")

    importlib.reload(runtime)
