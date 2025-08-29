import unittest, json, os
from unittest.mock import patch
from io import StringIO
from google.cloud import storage
from google.cloud.exceptions import NotFound
from hifi_solves_run_humanwgs.backends.gcp import (
    validate_bucket,
    check_file_exists,
    upload_files,
)
from hifi_solves_run_humanwgs.logger import logger

try:
    credentials_json_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_json_file is None:
        logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        raise SystemExit(1)
    with open(credentials_json_file, "r") as file:
        credentials = json.load(file)
    project_id = credentials.get("project_id", None)
    if project_id is None:
        logger.error("\t✗ GCP_PROJECT_ID was not found in the credentials JSON.")
        raise SystemExit(1)
    storage_client = storage.Client(project=project_id)
except json.JSONDecodeError:
    logger.error("\t✗ The credentials JSON is invalid.")
    raise SystemExit(1)
except ValueError as e:
    logger.error(e)
    raise SystemExit(1)


# These tests assume you are authenticated to GCP with a service account that has access to the test bucket
class TestValidateTargetBucket(unittest.TestCase):
    def test_bucket_exists_with_gs_prefix(self):
        bucket_name = "gs://hifi-solves-humanwgs-test-bucket"
        formatted_bucket, path_prefix = validate_bucket(bucket_name)
        self.assertEqual(formatted_bucket, "hifi-solves-humanwgs-test-bucket")
        self.assertEqual(path_prefix, None)

    def test_bucket_exists_no_gs_prefix(self):
        bucket_name = "hifi-solves-humanwgs-test-bucket"
        formatted_bucket, path_prefix = validate_bucket(bucket_name)
        self.assertEqual(formatted_bucket, f"{bucket_name}")
        self.assertEqual(path_prefix, None)

    def test_bucket_does_not_exist(self):
        bucket_name = "nonexistent-bucket"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_bucket(bucket_name)

        self.assertIn(
            "does not exist",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_bucket_exists_with_path(self):
        bucket_name = (
            "gs://hifi-solves-humanwgs-test-bucket/humanwgs_test/tabular_outputs"
        )
        formatted_bucket, path_prefix = validate_bucket(bucket_name)
        self.assertEqual(formatted_bucket, "hifi-solves-humanwgs-test-bucket")
        self.assertEqual(path_prefix, "humanwgs_test/tabular_outputs")


class TestCheckFileExists(unittest.TestCase):
    bucket_name = "hifi-solves-humanwgs-test-bucket"
    bucket_client = storage_client.bucket(bucket_name)
    bam_file = "HG002.bam"
    sample_id = "HG002"
    file_type = "bam"
    file_size_bytes = 12

    def setUp(self):
        with open(self.bam_file, "a") as f:
            # 12 bytes
            f.write("hello world\n")
        with open(self.bam_file, "rb") as data:
            blob = self.bucket_client.blob("my-custom-path/HG002.bam")
            blob.upload_from_file(data)
        with open(self.bam_file, "rb") as data:
            blob = self.bucket_client.blob("hifi-uploads/HG002/bam/HG002.bam")
            blob.upload_from_file(data)
        with open(self.bam_file, "rb") as data:
            blob = self.bucket_client.blob("HG002/bam/HG002.bam")
            blob.upload_from_file(data)

    def tearDown(self):
        os.remove(self.bam_file)
        custom_path_blob = self.bucket_client.blob("my-custom-path/HG002.bam")
        custom_path_blob.delete()
        hifi_uploads_blob = self.bucket_client.blob("hifi-uploads/HG002/bam/HG002.bam")
        hifi_uploads_blob.delete()
        sample_id_path_blob = self.bucket_client.blob("HG002/bam/HG002.bam")
        sample_id_path_blob.delete()

    # This is a different path than the one that the file would be uploaded to if a local path were provided
    def test_gcs_path_files_exist(self):
        path_prefix = None
        remote_file = f"gs://{self.bucket_name}/my-custom-path/HG002.bam"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket_name, path_prefix, remote_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "my-custom-path/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_gcs_path_files_dont_exist(self):
        path_prefix = "hifi-uploads"
        remote_file = f"gs://{self.bucket_name}/hifi-uploads/nonexistent/HG002.bam"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket_name,
            path_prefix,
            remote_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "hifi-uploads/nonexistent/HG002.bam")
        self.assertEqual(file_size_bytes, None)
        self.assertEqual(copy_status, None)

    def test_gcs_file_path_wrong_bucket(self):
        path_prefix = "hifi-uploads"
        remote_file = f"gs://wrong-bucket/hifi-uploads/HG002/bam/nonexistent/_HG002.bam"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            check_file_exists(
                self.bucket_name,
                path_prefix,
                remote_file,
                self.sample_id,
                self.file_type,
            )

        self.assertIn(
            "is outside of the target bucket",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_local_path_files_exist_with_path_prefix(self):
        path_prefix = "hifi-uploads"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket_name, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "hifi-uploads/HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_exist_no_path_prefix(self):
        path_prefix = None
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket_name, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_dont_exist(self):
        path_prefix = "nonexistent"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            self.bucket_name, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "nonexistent/HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, None)
        self.assertEqual(copy_status, None)


class TestUploadFiles(unittest.TestCase):
    bucket_name = "hifi-solves-humanwgs-test-bucket"
    bucket_client = storage_client.bucket(bucket_name)
    bam_file = "HG002.bam"
    remote_path = "hifi-uploads/HG002/bam/HG002.bam"

    def setUp(self):
        with open(self.bam_file, "a"):
            pass

    def tearDown(self):
        os.remove(self.bam_file)
        blob = self.bucket_client.blob("hifi-uploads/HG002/bam/HG002.bam")
        try:
            blob.delete()
        except NotFound:
            pass

    def test_upload_succeeded(self):
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="INFO") as log_capture:
            upload_files(self.bucket_name, files_to_upload)

        self.assertIn(
            "Uploading files to target bucket",
            log_capture.output[0],
        )

    def test_upload_failed_nonexistent_bucket(self):
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            upload_files("nonexistent-bucket", files_to_upload)

        self.assertIn(
            "does not exist",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_upload_failed(self):
        files_to_upload = {"nonexistent_file": self.remote_path}
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            upload_files(self.bucket_name, files_to_upload)

        self.assertIn(
            "Error uploading file",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
