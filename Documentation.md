# Documentation

## `main.py`

### Overview

This is the entry point of the application. It orchestrates the process of running a Docker container and sending its logs to AWS CloudWatch.

### Functions

- `parse_arguments()`: Parses command-line arguments using the argparse library. It defines the structure of the command-line input required to run the application, including the Docker image, bash command, CloudWatch log group and stream names, and AWS credentials.
- `main()`: The main function of the script. It calls `parse_arguments()` to parse the command-line arguments. Then, it tries to run a Docker container with the specified image and command, and set up CloudWatch logging for the container's output. If any exceptions occur during these operations, they are caught and handled by calling `handle_error()`.

## `utilities.py`

### Overview

Contains utility functions that can be used across different modules of the application.

### Functions

- `handle_error(e)`: Prints the provided error message to stderr. This function is designed to provide a unified way of handling errors throughout the application.

## `docker_manager.py`

### Overview

Manages interactions with Docker, including retrieving a Docker client and running containers.

### Functions

- `get_docker_client()`: Initializes and returns a Docker client from the environment. This client is used for all operations with Docker.
- `run_container(image_name, command)`: Tries to run a Docker container using the specified image and command. If successful, returns the container object. Errors during this process are caught and handled by `handle_error()`.

## `cloudwatch_manager.py`

### Overview

Manages interactions with AWS CloudWatch, including log group and log stream creation, and sending logs.

### Functions

- `create_cloudwatch_log_group(cloudwatch_client, group_name)`: Ensures the specified CloudWatch log group exists. If the group already exists, the operation is ignored. Errors are specifically handled based on their type.
- `create_cloudwatch_log_stream(cloudwatch_client, group_name, stream_name)`: Ensures the specified CloudWatch log stream exists within the given log group. If the stream already exists, the operation is ignored. Errors are specifically handled based on their type.
- `put_logs_to_cloudwatch(cloudwatch_client, group_name, stream_name, logs)`: Sends logs to the specified CloudWatch log stream. It handles the conversion of log messages to the format expected by CloudWatch, and manages the sequence token required for log events submission.
- `setup_cloudwatch_logging(container, args)`: Orchestrates the setup of CloudWatch logging. It initializes a CloudWatch client with the provided AWS credentials, ensures the existence of the specified log group and stream, and starts sending the container's logs to CloudWatch.

### How They Work Together

- **Starting Point (`main.py`)**: The process begins in `main.py` when the script is executed. Command-line arguments are parsed, and the main logic is initiated.
- **Running Docker Container (`docker_manager.py`)**: `main.py` calls `run_container` from `docker_manager.py` to start the Docker container with the specified image and command.
- **Setting Up CloudWatch Logging (`cloudwatch_manager.py`)**: Once the container is running, `main.py` calls `setup_cloudwatch_logging` from `cloudwatch_manager.py`. This function sets up the necessary CloudWatch log group and stream, then starts sending the container's logs to CloudWatch.
- **Error Handling (`utilities.py`)**: Throughout this process, any errors that occur are handled by calling `handle_error` from `utilities.py`, ensuring that error messages are consistently logged to stderr.

This architecture separates concerns across different modules, making the code more maintainable and modular. The `utilities.py` module provides shared functionality (error handling), `docker_manager.py` abstracts Docker interactions, and `cloudwatch_manager.py` handles AWS CloudWatch operations, with `main.py` orchestrating the overall process.