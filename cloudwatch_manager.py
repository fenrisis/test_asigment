import boto3
import time
import logging
from botocore.exceptions import ClientError, ParamValidationError
from utilities import handle_error
from concurrent.futures import ThreadPoolExecutor

BATCH_SIZE = 10  # Adjustable value for the number of logs to send at once

def create_cloudwatch_log_group(cloudwatch_client, group_name):
    # Attempts to create a CloudWatch log group
    try:
        cloudwatch_client.create_log_group(logGroupName=group_name)
        logging.info(f"Created CloudWatch log group: {group_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            logging.info(f"Log group already exists: {group_name}, ignoring...")
        else:
            raise

def create_cloudwatch_log_stream(cloudwatch_client, group_name, stream_name):
    # Attempts to create a CloudWatch log stream
    try:
        cloudwatch_client.create_log_stream(logGroupName=group_name, logStreamName=stream_name)
        logging.info(f"Created CloudWatch log stream: {stream_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            logging.info(f"Log stream already exists: {stream_name}, ignoring...")
        else:
            raise

def send_log_events(cloudwatch_client, group_name, stream_name, log_events, sequence_token=None):
    # Sends a batch of log events to CloudWatch
    try:
        request_params = {
            'logGroupName': group_name,
            'logStreamName': stream_name,
            'logEvents': log_events
        }
        if sequence_token:
            request_params['sequenceToken'] = sequence_token

        cloudwatch_client.put_log_events(**request_params)
        logging.info(f"Sent log events to CloudWatch: {group_name}/{stream_name}")
    except ClientError as e:
        logging.error("ClientError during put_log_events", exc_info=True)
    except ParamValidationError as e:
        logging.error("ParamValidationError during put_log_events", exc_info=True)

def put_logs_to_cloudwatch(cloudwatch_client, group_name, stream_name, logs):
    # Uses a thread pool to send logs asynchronously
    logging.info(f"Starting to send logs to CloudWatch: {group_name}/{stream_name}")
    with ThreadPoolExecutor(max_workers=5) as executor:
        log_events = []
        for log in logs:
            message = log.decode('utf-8') if isinstance(log, bytes) else log
            timestamp = int(time.time() * 1000)
            log_events.append({'timestamp': timestamp, 'message': message})

            if len(log_events) >= BATCH_SIZE:
                # Describe log streams to get the sequence token
                response = cloudwatch_client.describe_log_streams(logGroupName=group_name, logStreamNamePrefix=stream_name)
                streams = response.get('logStreams', [])
                sequence_token = streams[0].get('uploadSequenceToken') if streams else None

                # Submit log events for sending
                executor.submit(send_log_events, cloudwatch_client, group_name, stream_name, log_events.copy(), sequence_token)
                log_events.clear()

        # Send remaining log events that didn't reach BATCH_SIZE
        if log_events:
            response = cloudwatch_client.describe_log_streams(logGroupName=group_name, logStreamNamePrefix=stream_name)
            streams = response.get('logStreams', [])
            sequence_token = streams[0].get('uploadSequenceToken') if streams else None
            executor.submit(send_log_events, cloudwatch_client, group_name, stream_name, log_events, sequence_token)

def setup_cloudwatch_logging(container, args):
    # Configures logging to AWS CloudWatch
    try:
        logging.info("Setting up CloudWatch logging")
        cloudwatch_client = boto3.client(
            'logs',
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            region_name=args.aws_region
        )

        create_cloudwatch_log_group(cloudwatch_client, args.cloudwatch_group)
        create_cloudwatch_log_stream(cloudwatch_client, args.cloudwatch_group, args.cloudwatch_stream)

        # Fetch container logs and send them to CloudWatch
        logs = container.logs(stream=True, follow=True)
        put_logs_to_cloudwatch(cloudwatch_client, args.cloudwatch_group, args.cloudwatch_stream, logs)

    except Exception as e:
        handle_error(e)
