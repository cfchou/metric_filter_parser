import pytest
import boto3

@pytest.fixture()
def client():
    return boto3.client('logs')


