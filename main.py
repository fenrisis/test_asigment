import argparse
import logging
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
    args = parse_arguments()
    container = None
    try:
        container = run_container(args.docker_image, args.bash_command)
        setup_cloudwatch_logging(container, args)
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
    finally:
        if container:
            try:
                logging.info(f"Attempting to remove container {container.id} due to cleanup...")
                docker_client = get_docker_client()
                docker_client.containers.get(container.id).remove(force=True)
                logging.info(f"Container {container.id} successfully removed.")
            except Exception as cleanup_error:
                logging.error("Failed to remove container:", exc_info=True)


if __name__ == "__main__":
    main()
