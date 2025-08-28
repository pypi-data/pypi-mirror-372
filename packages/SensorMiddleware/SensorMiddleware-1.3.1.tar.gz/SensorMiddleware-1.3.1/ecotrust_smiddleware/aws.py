from contextlib import contextmanager
from typing import AnyStr, Union, Dict, NoReturn, List
from botocore.client import BaseClient
from rich import print # noqa

import boto3
import json
import os

DEBUG = os.getenv('DEBUG', False)

# AWS CONFIG ENVS
AWS_REGION_NAME = os.getenv('S3_REGION', 'us-east-1')
AWS_SQS_BASE_URL = os.getenv('SQS_BASE_QUEUE_URL')

# S3 AWS ENV CONFIG
S3_SCAN_BUCKET = os.getenv('S3_BUCKET')
S3_SCAN_DATA_PATH = os.getenv('S3_SCAN_DATA_URI_PATH')
S3_SCAN_REPORT_PATH = os.getenv('S3_SCAN_REPORT_URI_PATH')
S3_URI_SPLIT = S3_SCAN_REPORT_PATH.split('/')
TENANT = S3_URI_SPLIT[0]
S3_SCAN_LOG_URI = f'tempdata/scans-log/{TENANT}'

# AWS CREDS
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')


class Boto3SessionManager:
    _session = None

    @classmethod
    def get_session(cls) -> boto3.Session:
        #if cls._session is None:
            # Create session

        # create session every time to solve 'credentials were refreshed, but the refreshed credentials are still expired'
        # not the best fix, but we need it :/
        cls._session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION_NAME
        )

        # Return session
        return cls._session


@contextmanager
def access_aws_resource(session: boto3.Session, resource_name: AnyStr) -> BaseClient:
    """
        Access AWS resource with boto3 client.
    :param session:
    :param resource_name:
    :return: Client for the resource
    """
    yield session.client(resource_name)


def send_sqs_message(queue: AnyStr, message: Dict) -> NoReturn:
    """
    Sends a message to SQS queue.
    :param queue:
    :param message:
    :return:
    """
    with access_aws_resource(Boto3SessionManager.get_session(), 'sqs') as sqs_client:
        _ = sqs_client.send_message(
            QueueUrl=AWS_SQS_BASE_URL.format(queue),
            MessageBody=json.dumps(message, default=str)
        )

    return


def upload_report_to_s3_bucket(
        report:  Union[str, Dict],
        scan_id: Union[int, str, None] = None,
        is_crash_dump=False) -> NoReturn:
    """
    Uploads a file to S3 bucket.
    :param report: Scan report typed as Dict.
    :param scan_id: ID of the current running scan.
    :param is_crash_dump: If is a crash dump, store in a differente place on S3 Bucket.
    :return:
    """
    if is_crash_dump:
        # Raw string body
        assert scan_id is not None, 'null scan_id'

        key_to_store = f'{S3_SCAN_LOG_URI}/{scan_id}/crashdump.log'
        body_to_store = report
    else:
        key_to_store = S3_SCAN_REPORT_PATH
        body_to_store = json.dumps(report, default=str)

    with access_aws_resource(Boto3SessionManager.get_session(), 's3') as s3_client:
        s3_response = s3_client.put_object(
            ACL='private',
            Bucket=S3_SCAN_BUCKET,
            Key=key_to_store,
            Body=body_to_store
        )

        if DEBUG:
            print(f'[bold green] Sent json report to S3, response: {str(s3_response)}')

    return


def upload_log_dump(files: List[str], scan_id: int) -> NoReturn:
    """
        Uploads logs for post analysis
        Dir: bucket/tempdata/scans-log/{tenant}/{scan_id}/LOGS[@]
    :param files: List of files to upload.
    :param scan_id: ID of the current running scan.
    :return:
    """
    for f in files:
        if not os.path.exists(f):
            continue

        filename = os.path.basename(f)
        with access_aws_resource(Boto3SessionManager.get_session(), 's3') as s3_client:
            s3_response = s3_client.upload_file(
                Filename=f,
                Bucket=S3_SCAN_BUCKET,
                Key=f'{S3_SCAN_LOG_URI}/{scan_id}/{filename}')

            if DEBUG:
                print(f'[bold green] Sent debug file to s3, response: {str(s3_response)}')


def get_scan_data_from_s3_bucket() -> Dict:
    """
        Get Scan metadata from S3 using predefined envvars by ECS Fargate

    :return: scan_data -> Dict object containing metadata information about the Scan to be run.
    """
    if any(v is None for v in [S3_SCAN_BUCKET, S3_SCAN_DATA_PATH]):
        raise RuntimeError('Cannot get scan data (null BUCKET/DATA_PATH)')

    with access_aws_resource(Boto3SessionManager.get_session(), 's3') as s3_client:

        response = s3_client.get_object(
            Bucket=S3_SCAN_BUCKET,
            Key=S3_SCAN_DATA_PATH,
        )

        scan_data = json.load(response['Body'])
        if DEBUG:
            print(f'[bold green] Got scan info: {str(scan_data)} [/bold green]')

    return scan_data
