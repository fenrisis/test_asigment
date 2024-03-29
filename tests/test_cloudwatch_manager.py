import pytest
from cloudwatch_manager import create_cloudwatch_log_group
from botocore.exceptions import ClientError
from unittest.mock import MagicMock, patch


def make_client_error(code):
    return ClientError({"Error": {"Code": code}}, "operation_name")


@patch('cloudwatch_manager.boto3.client')
def test_create_cloudwatch_log_group_already_exists(mock_boto_client):
    # Mock ClientError to simulate an existing group of logs
    mock_boto_client.return_value.create_log_group.side_effect = make_client_error('ResourceAlreadyExistsException')

    # call the function, expecting that the error will be handled correctly
    create_cloudwatch_log_group(mock_boto_client.return_value, "test-log-group")

    # make sure that create_log_group was called with the correct group name
    mock_boto_client.return_value.create_log_group.assert_called_once_with(logGroupName="test-log-group")


@patch('cloudwatch_manager.boto3.client')
def test_create_cloudwatch_log_group_raises(mock_boto_client):
    # Mock ClientError to simulate another error
    mock_boto_client.return_value.create_log_group.side_effect = make_client_error('AnotherException')

    # Call the function expecting the error
    with pytest.raises(ClientError):
        create_cloudwatch_log_group(mock_boto_client.return_value, "test-log-group")
