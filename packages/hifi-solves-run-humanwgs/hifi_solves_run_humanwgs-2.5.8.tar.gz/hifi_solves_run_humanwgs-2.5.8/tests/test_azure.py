import unittest
from unittest.mock import patch
from io import StringIO
import os
import re
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from hifi_solves_run_humanwgs.backends.azure import (
    _get_credential,
    validate_bucket,
    check_file_exists,
    check_file_exists_remote_src,
    transfer_files,
    upload_files,
)
from hifi_solves_run_humanwgs.logger import logger

# dest container
storage_account = "bioscoastorage"
container_name = "hifi-solves-humanwgs-test-bucket"
blob_container = f"{storage_account}/{container_name}"

# src container
src_storage_account = "iceberg"
src_container_name = "hifi-solves-humanwgs-test-src-bucket"
blob_src_container = f"{src_storage_account}/{src_container_name}"

credential = _get_credential()
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account}.blob.core.windows.net",
    credential=credential,
)


class TestGetCredential(unittest.TestCase):
    def test_get_credential_dest(self):
        _ = _get_credential()

    def test_get_credential_src(self):
        _ = _get_credential(target_container="src")

    def test_get_credential_missing_dest_variable(self):
        with patch.dict(os.environ, clear=True):
            with self.assertLogs(
                logger, level="ERROR"
            ) as log_capture, self.assertRaises(SystemExit) as exit_capture:
                _get_credential(target_container="dest")

            self.assertIn(
                "Must set and export the AZURE_STORAGE_SAS_TOKEN env variable",
                log_capture.output[0],
            )
            self.assertEqual(exit_capture.exception.code, 1)

    def test_get_credential_missing_src_variable(self):
        with patch.dict(os.environ, clear=True):
            with self.assertLogs(
                logger, level="ERROR"
            ) as log_capture, self.assertRaises(SystemExit) as exit_capture:
                _get_credential(target_container="src")

            self.assertIn(
                "Must set and export the SOURCE_CONTAINER_SAS_TOKEN env variable",
                log_capture.output[0],
            )
            self.assertEqual(exit_capture.exception.code, 1)

    def test_credential_expired(self):
        epoch_iso = "1970-01-01T00:00:00Z"
        expired_sas_token = re.sub(
            "se=[^&]*", f"se={epoch_iso}", os.getenv("AZURE_STORAGE_SAS_TOKEN")
        )
        with patch.dict(
            os.environ, {"AZURE_STORAGE_SAS_TOKEN": expired_sas_token}, clear=True
        ):
            with self.assertLogs(
                logger, level="ERROR"
            ) as log_capture, self.assertRaises(SystemExit) as exit_capture:
                _get_credential(target_container="dest")

            self.assertIn(
                "AZURE_STORAGE_SAS_TOKEN is expired; please contact your administrator to get a new token.",
                log_capture.output[0],
            )
            self.assertEqual(exit_capture.exception.code, 1)


class TestValidateContainer(unittest.TestCase):
    def test_container_exists(self):
        formatted_container, path_prefix = validate_bucket(blob_container)
        self.assertEqual(formatted_container, blob_container)
        self.assertEqual(path_prefix, None)

    def test_container_does_not_exist(self):
        container = "hifi-solves-test-container"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_bucket(f"{storage_account}/{container}")

        self.assertIn(
            "Authentication failed",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_container_exists_with_path(self):
        formatted_container, path_prefix = validate_bucket(
            f"{blob_container}/hifi-uploads/my_path"
        )
        self.assertEqual(formatted_container, blob_container)
        self.assertEqual(path_prefix, "hifi-uploads/my_path")


class TestCheckFileExists(unittest.TestCase):
    bam_file = "HG002.bam"
    sample_id = "HG002"
    file_type = "bam"
    file_size_bytes = 12

    def setUp(self):
        with open(self.bam_file, "a") as f:
            # 12 bytes
            f.write("hello world\n")

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="my-custom-path/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="hifi-uploads/HG002/bam/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="HG002/bam/HG002.bam",
        )
        with open(self.bam_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def tearDown(self):
        os.remove(self.bam_file)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="my-custom-path/HG002.bam",
        )
        blob_client.delete_blob()

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="hifi-uploads/HG002/bam/HG002.bam",
        )
        blob_client.delete_blob()

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob="HG002/bam/HG002.bam",
        )
        blob_client.delete_blob()

    def test_blob_path_files_exist(self):
        path_prefix = None
        remote_file = f"/{blob_container}/my-custom-path/HG002.bam"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            blob_container,
            path_prefix,
            remote_file,
            self.sample_id,
            self.file_type,
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "my-custom-path/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_blob_path_files_dont_exist(self):
        path_prefix = "hifi-uploads"
        remote_file = f"/{blob_container}/hifi-uploads/nonexistent/HG002.bam"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            blob_container, path_prefix, remote_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "hifi-uploads/nonexistent/HG002.bam")
        self.assertEqual(file_size_bytes, None)
        self.assertEqual(copy_status, None)

    def test_blob_path_wrong_container(self):
        path_prefix = "hifi-uploads"
        remote_file = f"/{storage_account}/wrong_container/hifi-uploads/HG002.bam"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            check_file_exists(
                blob_container, path_prefix, remote_file, self.sample_id, self.file_type
            )

        self.assertIn(
            "is outside of the target container.",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_local_path_files_exist_with_path_prefix(self):
        path_prefix = "hifi-uploads"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(
            remote_path,
            "hifi-uploads/HG002/bam/HG002.bam",
        )
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_exist_no_path_prefix(self):
        path_prefix = None
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, True)
        self.assertEqual(remote_path, "HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, self.file_size_bytes)
        self.assertEqual(copy_status, None)

    def test_local_path_files_dont_exist(self):
        path_prefix = "nonexistent"
        file_exists, remote_path, file_size_bytes, copy_status = check_file_exists(
            blob_container, path_prefix, self.bam_file, self.sample_id, self.file_type
        )
        self.assertEqual(file_exists, False)
        self.assertEqual(remote_path, "nonexistent/HG002/bam/HG002.bam")
        self.assertEqual(file_size_bytes, None)
        self.assertEqual(copy_status, None)


# Azure <> Azure - check if files exist at src remote
# Our src storage account doesn't have write, so we can't setup/teardown automatically
# Just using files that are already hosted in this bucket
class TestCheckFileExistsRemoteSrc(unittest.TestCase):
    def test_remote_src_file_exists(self):
        file_path = f"/{blob_src_container}/my/bam/path/_HG002.bam"
        file_exists, file_size_bytes = check_file_exists_remote_src(file_path)
        self.assertEqual(file_exists, True)
        self.assertEqual(file_size_bytes, 23)

    def test_remote_src_files_dont_exist(self):
        file_path = f"/{blob_src_container}/nonexistent/_HG002.bam"
        file_exists, file_size_bytes = check_file_exists_remote_src(file_path)
        self.assertEqual(file_exists, False)
        self.assertEqual(file_size_bytes, None)

    def test_blob_path_wrong_container(self):
        file_path = f"/{src_storage_account}/wrong_container/my/bam/path/_HG002.bam"
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            check_file_exists_remote_src(file_path)

        self.assertIn(
            "✗ Azure configuration error: ",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


# Azure <> Azure - transfer files from one storage account to another
class TestTransferFiles(unittest.TestCase):
    remote_path = "test/hifi-uploads/HG002.bam"

    def tearDown(self):
        try:
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=self.remote_path
            )
            blob_client.delete_blob()
        except ResourceNotFoundError:
            # If the blob or container doesn't exist, ignore the error
            pass

    def test_transfer_succeeded(self):
        files_to_transfer = {
            f"/{blob_src_container}/my/bam/path/_HG002.bam": self.remote_path
        }
        with self.assertLogs(logger, level="INFO") as log_capture:
            transfer_files(blob_container, files_to_transfer)

        self.assertIn(
            "Transferring files from src to target container",
            log_capture.output[0],
        )

    def test_dest_container_does_not_exist(self):
        files_to_transfer = {
            f"/{blob_src_container}/my/bam/path/_HG002.bam": self.remote_path
        }
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            transfer_files(
                f"{storage_account}/nonexistent_container", files_to_transfer
            )

        self.assertIn(
            "Authentication failed; do src and dest containers exist?",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_src_file_does_not_exist(self):
        files_to_transfer = {
            f"/{blob_src_container}/my/nonexistent/path/_HG002.bam": self.remote_path
        }
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            transfer_files(blob_container, files_to_transfer)

        self.assertIn(
            "Failed to find remote src file",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


class TestUploadFiles(unittest.TestCase):
    bam_file = "HG002.bam"
    remote_path = "test/hifi-uploads/HG002.bam"

    def setUp(self):
        with open(self.bam_file, "a"):
            pass

    def tearDown(self):
        try:
            os.remove(self.bam_file)
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=self.remote_path
            )
            blob_client.delete_blob()
        except ResourceNotFoundError:
            # If the blob or container doesn't exist, ignore the error
            pass

    def test_upload_succeeded(self):
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="INFO") as log_capture:
            upload_files(blob_container, files_to_upload)

        self.assertIn(
            "Uploading files to target container",
            log_capture.output[0],
        )

    def test_upload_failed(self):
        nonexistent_container = "nonexistent-container"
        files_to_upload = {self.bam_file: self.remote_path}
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            upload_files(f"{storage_account}/{nonexistent_container}", files_to_upload)

        self.assertIn(
            "Authentication failed",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
