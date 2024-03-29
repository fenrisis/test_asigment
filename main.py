import argparse
import logging
import threading
from docker_manager import run_container, get_docker_client
from cloudwatch_manager import setup_cloudwatch_logging
from utilities import handle_error
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='Run a Docker container and send logs to AWS CloudWatch.')
    parser.add_argument('docker_image', help='Name of the Docker image to use')
    parser.add_argument('bash_command', help='Bash command to run inside the Docker container')
    parser.add_argument('cloudwatch_group', help='Name of the AWS CloudWatch log group')
    parser.add_argument('cloudwatch_stream', help='Name of the AWS CloudWatch log stream')
    parser.add_argument('aws_access_key_id', help='AWS access key id')
    parser.add_argument('aws_secret_access_key', help='AWS secret access key')
    parser.add_argument('aws_region', help='AWS region to use')
    return parser.parse_args()

# Main function
def main():
    """Main function to run the container and setup CloudWatch logging."""
    args = parse_arguments()
    container = None
    try:
        container = run_container(args.docker_image, args.bash_command)
        # Start the CloudWatch logging setup in a separate thread to allow concurrent execution.
        logging_thread = threading.Thread(target=setup_cloudwatch_logging, args=(container, args))
        logging_thread.start()
        # Removed join here to not block the main thread; logs and container will run concurrently.
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
    finally:
        if container:
            # Optionally wait for the logging to finish before removing the container.
            # This would ensure all logs are sent before cleanup.
            logging_thread.join()  # Wait for the logging thread to finish if it was successfully started.
            try:
                logging.info(f"Attempting to remove container {container.id} due to cleanup...")
                docker_client = get_docker_client()
                docker_client.containers.get(container.id).remove(force=True)
                logging.info(f"Container {container.id} successfully removed.")
            except Exception as cleanup_error:
                logging.error("Failed to remove container:", exc_info=True)

if __name__ == "__main__":
    main()
