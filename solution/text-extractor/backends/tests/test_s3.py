import unittest

import boto3
import mock
from moto import mock_s3

from backends import (
    BackendException,
    BackendInitException,
    FileBackend,
    S3Backend,
)


class TestS3Backend(unittest.TestCase):
    BUCKET_NAME = "some_bucket"
    FILE_NAME = "some_file"
    FILE_BODY = b"This is some content"

    POST_PARAMS = {
        "s3": {
            "aws_access_key_id": "some_id",
            "aws_secret_access_key": "some_key",
            "aws_storage_bucket_name": BUCKET_NAME,
        },
    }

    def setUp(self):
        self.mock_s3 = mock_s3()
        self.mock_s3.start()

        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=self.BUCKET_NAME)
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket=self.BUCKET_NAME, Key="some_file", Body=self.FILE_BODY)

    def test_create_backend(self):
        backend = FileBackend.get_backend("s3", self.POST_PARAMS)
        self.assertIsInstance(backend, S3Backend)

    def test_required_keys(self):
        with self.assertRaises(BackendInitException):
            S3Backend({})

        for i in ["aws_access_key_id", "aws_secret_access_key", "aws_storage_bucket_name"]:
            params = self.POST_PARAMS.copy()
            del params["s3"][i]
            with self.assertRaises(BackendInitException):
                S3Backend(params)

    def test_client_create_exception(self):
        with mock.patch.object(boto3, "client") as client_mock:
            client_mock.side_effect = Exception("Something happened")
            with self.assertRaises(BackendInitException):
                S3Backend(self.POST_PARAMS)

    def test_get_file(self):
        backend = S3Backend(self.POST_PARAMS)
        file = backend.get_file(self.FILE_NAME)
        self.assertEqual(file, self.FILE_BODY)

    def test_bad_key(self):
        backend = S3Backend(self.POST_PARAMS)
        with self.assertRaises(BackendException):
            backend.get_file("invalid_key")
