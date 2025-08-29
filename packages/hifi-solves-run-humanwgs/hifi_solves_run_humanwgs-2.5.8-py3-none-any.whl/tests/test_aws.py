import unittest
from unittest.mock import patch
from io import StringIO
import os
import boto3
from hifi_solves_run_humanwgs.backends.aws import (
    validate_bucket,
    check_file_exists,
    upload_files,
)
from hifi_solves_run_humanwgs.logger import logger


# These tests assume you are authenticated to AWS with a profile that has access to the test buckets
class TestValidateTargetBucket(unittest.TestCase):
    def test_bucket_exists_with_s3_prefix(self):
        bucket = "s3://hifi-solves-humanwgs-test-bucket"
        formatted_bucket, path_prefix = validate_bucket(bucket)
        self.assertEqual(formatted_bucket, "hifi-solves-humanwgs-test-bucket")
        self.assertEqual(path_prefix, None)

    def test_bucket_exists_no_s3_prefix(self):
        bucket = "hifi-solves-humanwgs-test-bucket"
        formatted_bucket, path_prefix = validate_bucket(bucket)
        self.assertEqual(formatted_bucket, "hifi-solves-humanwgs-test-bucket")
        self.assertEqual(path_prefix, None)

    def test_bucket_does_not_exist(self):
        bucket = "HIFI-SOLVES-HUMANWGS-TEST-BUCKET"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_bucket(bucket)

        self.assertIn(
            "does not exist",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_bucket_exists_with_path(self):
        bucket = "s3://hifi-solves-humanwgs-test-bucket/hifi-uploads/my_path/"
        formatted_bucket, path_prefix = validate_bucket(bucket)
        self.assertEqual(formatted_bucket, "hifi-solves-humanwgs-test-bucket")
        self.assertEqual(path_prefix, "hifi-uploads/my_path")


class TestCheckFileExists(unittest.TestCase):
    s3_client = boto3.client("s3")
    bam_file = "_HG002.bam"
    bucket = "hifi-solves-humanwgs-test-bucket"
    sample_id = "HG002"
    file_type = "bam"
    file_size_bytes = 12

    def setUp(self):
        with open(self.bam_file, "a") as f:
            # 12 bytes
            f.write("hello world\n")
        self.s3_client.upload_file(
            self.bam_file, self.bucket, "my-custom-path/_HG002.bam"
        )
        self.s3_client.upload_file(
            self.bam_file, self.bucket, "hifi-uploads/HG002/bam/_HG002.bam"
        )
        self.s3_client.upload_file(self.bam_file, self.bucket, "HG002/bam/_HG002.bam")

    def tearDown(self):
        os.remove(self.bam_file)
        self.s3_client.delete_object(
            Bucket=self.bucket, Key="my-custom-path/_HG002.bam"
        )
        self.s3_client.delete_object(
            Bucket=self.bucket, Key="hifi-uploads/HG002/bam/_HG002.bam"
        )
        self.s3_client.delete_object(Bucket=self.bucket, Key="HG002/bam/_HG002.bam")

    # This is a different path than the one that the file would be uploaded to if a local path were provided
    def test_s3_path_files_exist(self):
        path_prefix = None
        remote_file = f"s3://{self.bucket}/my-custom-path/_HG002.bam"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket, path_prefix, remote_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "my-custom-path/_HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_s3_path_files_dont_exist(self):
        path_prefix = "hifi-uploads"
        remote_file = (
            f"s3://{self.bucket}/hifi-uploads/HG002/bam/nonexistent/_HG002.bam"
        )
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket, path_prefix, remote_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "hifi-uploads/HG002/bam/nonexistent/_HG002.bam")
        self.assertEqual(file_size_bytes, None),
        self.assertEqual(copy_status, None)

    def test_s3_path_wrong_bucket(self):
        path_prefix = "hifi-uploads"
        remote_file = f"s3://different-target-bucket/hifi-uploads/HG002/bam/nonexistent/_HG002.bam"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            check_file_exists(
                self.bucket,
                path_prefix,
                remote_file,
                self.sample_id,
                self.file_type,
            )

        self.assertIn(
            "is outside of the target bucket.",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_local_path_files_exist_with_path_prefix(self):
        path_prefix = "hifi-uploads"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket,
            path_prefix,
            self.bam_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "hifi-uploads/HG002/bam/_HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_exist_no_path_prefix(self):
        path_prefix = None
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket,
            path_prefix,
            self.bam_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "HG002/bam/_HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_dont_exist(self):
        path_prefix = "nonexistent"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket,
            path_prefix,
            self.bam_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "nonexistent/HG002/bam/_HG002.bam")
        self.assertEqual(file_size_bytes, None)
        self.assertEqual(copy_status, None)


class TestUploadFiles(unittest.TestCase):
    s3_client = boto3.client("s3")
    bam_file = "_HG002.bam"
    bucket = "hifi-solves-humanwgs-test-bucket"
    remote_path = "hifi-uploads/HG002/bam/_HG002.bam"

    def setUp(self):
        with open(self.bam_file, "a"):
            pass

    def tearDown(self):
        os.remove(self.bam_file)
        self.s3_client.delete_object(Bucket=self.bucket, Key=self.remote_path)

    def test_upload_succeeded(self):
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="INFO") as log_capture:
            upload_files(self.bucket, files_to_upload)

        self.assertIn(
            f"Uploading files to target bucket",
            log_capture.output[0],
        )

    def test_upload_failed(self):
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            upload_files("nonexistent-bucket", files_to_upload)

        self.assertIn(
            "Error uploading file",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
