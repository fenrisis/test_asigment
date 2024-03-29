import pytest
from docker_manager import run_container, get_docker_client
from docker.errors import ContainerError, ImageNotFound
from unittest.mock import patch, MagicMock

@patch('docker_manager.get_docker_client')
def test_run_container_success(mock_get_docker_client):
    mock_docker = MagicMock()
    mock_get_docker_client.return_value = mock_docker
    mock_container = MagicMock()
    mock_docker.containers.run.return_value = mock_container
    container = run_container('python:3.8-slim', 'echo hello world')
    mock_docker.containers.run.assert_called_once_with('python:3.8-slim', 'echo hello world', detach=True)
    assert container is mock_container

@patch('docker_manager.handle_error')
@patch('docker_manager.get_docker_client')
def test_run_container_failure(mock_get_docker_client, mock_handle_error):
    mock_docker = MagicMock()
    mock_get_docker_client.return_value = mock_docker
    mock_docker.containers.run.side_effect = ImageNotFound('image not found')
    run_container('python:3.8-slim', 'echo hello world')
    mock_handle_error.assert_called_once()

