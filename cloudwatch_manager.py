import boto3
import time
import logging
from botocore.exceptions import ClientError, ParamValidationError
from utilities import handle_error

def create_cloudwatch_log_group(cloudwatch_client, group_name):
    try:
        cloudwatch_client.create_log_group(logGroupName=group_name)
        logging.info(f"Created CloudWatch log group: {group_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            logging.info(f"Log group already exists: {group_name}, ignoring...")
        else:
            raise

def create_cloudwatch_log_stream(cloudwatch_client, group_name, stream_name):
    try:
        cloudwatch_client.create_log_stream(logGroupName=group_name, logStreamName=stream_name)
        logging.info(f"Created CloudWatch log stream: {stream_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            logging.info(f"Log stream already exists: {stream_name}, ignoring...")
        else:
            raise

def put_logs_to_cloudwatch(cloudwatch_client, group_name, stream_name, logs):
    try:
        log_events = []
        for log in logs:
            message = log.decode('utf-8') if isinstance(log, bytes) else log
            timestamp = int(time.time() * 1000)
            log_events.append({'timestamp': timestamp, 'message': message})

        response = cloudwatch_client.describe_log_streams(logGroupName=group_name, logStreamNamePrefix=stream_name)
        streams = response.get('logStreams', [])
        sequence_token = None
        if streams:
            sequence_token = streams[0].get('uploadSequenceToken')

        logging.info(f"Sending logs to CloudWatch: {group_name}/{stream_name}")
        if sequence_token:
            cloudwatch_client.put_log_events(
                logGroupName=group_name,
                logStreamName=stream_name,
                logEvents=log_events,
                sequenceToken=sequence_token
            )
        else:
            cloudwatch_client.put_log_events(
                logGroupName=group_name,
                logStreamName=stream_name,
                logEvents=log_events
            )
    except ParamValidationError as e:
        logging.error(f"Error: The parameters you provided are incorrect: {e}")
    except ClientError as e:
        handle_error(e)


def setup_cloudwatch_logging(container, args):
    try:
        logging.info("Setting up CloudWatch logging")
        # Create CloudWatch client
        cloudwatch_client = boto3.client(
            'logs',
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            region_name=args.aws_region
        )

        # Ensure the CloudWatch log group exists
        create_cloudwatch_log_group(cloudwatch_client, args.cloudwatch_group)

        # Ensure the CloudWatch log stream exists
        create_cloudwatch_log_stream(cloudwatch_client, args.cloudwatch_group, args.cloudwatch_stream)

        # Fetch the logs of the container and send them to CloudWatch
        logs = container.logs(stream=True, follow=True)
        put_logs_to_cloudwatch(cloudwatch_client, args.cloudwatch_group, args.cloudwatch_stream, logs)

    except Exception as e:
        handle_error(e)
