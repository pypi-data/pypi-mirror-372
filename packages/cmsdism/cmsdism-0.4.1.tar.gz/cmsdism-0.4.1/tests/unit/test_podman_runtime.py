from unittest.mock import MagicMock, patch

import pytest

from dismcli.lib.start_api.runtimes.runtime import runtime_factory


@pytest.fixture(autouse=True)
def patch_podman_socket(monkeypatch):
    """Avoid calling real systemctl in PodmanRuntime."""
    monkeypatch.setattr(
        "dismcli.lib.start_api.runtimes.podman_runtime.PodmanRuntime._is_podman_installed",
        lambda self: True,
    )
    monkeypatch.setattr(
        "dismcli.lib.start_api.runtimes.podman_runtime.PodmanRuntime._is_podman_socket_active",
        lambda self: True,
    )
    monkeypatch.setattr(
        "dismcli.lib.start_api.runtimes.podman_runtime.shutil.which",
        lambda name: "/usr/bin/systemctl",  # fake path
    )
    monkeypatch.setattr(
        "dismcli.lib.start_api.runtimes.podman_runtime.subprocess.check_output",
        lambda *a, **kw: "active",
    )


@pytest.fixture
def mock_podman_client():
    with patch("dismcli.lib.start_api.runtimes.podman_runtime.podman.PodmanClient") as mock_podman:
        yield mock_podman.return_value


@pytest.fixture
def container_instance(mock_podman_client):
    args = {"image": "test_image", "detach": True}
    container_cls = runtime_factory(runtime="podman")
    return container_cls(args)


def test_container_init(container_instance, mock_podman_client):
    assert container_instance.args == {"image": "test_image", "detach": True}
    assert container_instance.client == mock_podman_client
    assert container_instance.container is None


def test_run_starts_container(container_instance, mock_podman_client):
    mock_container = MagicMock()
    mock_podman_client.containers.run.return_value = mock_container

    with patch("dismcli.lib.start_api.runtimes.podman_runtime.signal.signal") as mock_signal:
        container_instance.run()

    mock_podman_client.containers.run.assert_called_once_with(**container_instance.args)
    mock_signal.assert_called_once()
    mock_container.logs.assert_called_once_with(stream=True, follow=True, stdout=True, stderr=True)


def test_run_handles_exception(container_instance, mock_podman_client):
    mock_podman_client.containers.run.side_effect = Exception("Test error")
    with patch.object(container_instance, "cleanup") as mock_cleanup:
        container_instance.run()

    mock_cleanup.assert_called_once()


def test_cleanup_stops_and_removes_container(container_instance):
    mock_container = MagicMock()
    container_instance.container = mock_container

    container_instance.cleanup()

    mock_container.stop.assert_called_once()


def test_cleanup_no_container(container_instance):
    container_instance.container = None
    # should not raise
    container_instance.cleanup()
