import docker
import logging
from utilities import handle_error

def get_docker_client():
    return docker.from_env()

def run_container(image_name, command):
    docker_client = get_docker_client()
    container = None
    try:
        logging.info(f"Attempting to run container with image: {image_name} and command: '{command}'")
        container = docker_client.containers.run(image_name, command, detach=True)
        logging.info(f"Container {container.id} is running.")
        return container
    except Exception as e:
        logging.error(f"Failed to run container: {e}", exc_info=True)
        if container:
            try:
                logging.info(f"Attempting to remove container {container.id} due to an error.")
                container.remove(force=True)
                logging.info(f"Container {container.id} removed successfully.")
            except Exception as cleanup_error:
                logging.error(f"Failed to remove container: {cleanup_error}", exc_info=True)
                handle_error(cleanup_error)
        handle_error(e)
        raise e