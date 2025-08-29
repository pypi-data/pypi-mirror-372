import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceRequestError,
)
from urllib.parse import unquote
from datetime import datetime, timezone
import regex as re
from ..logger import logger


def _get_credential(target_container="dest"):
    """
    Get Azure credentials using a SAS token

    Args:
        target_container (str): Target container to get credentials for; determines which env variable to use to look for the SAS token
                                Available options are ["src", "dest"]. ["dest"]

    Returns:
        credential (AzureSasCredential): credential used to auth with Azure
    """
    if target_container == "dest":
        sas_token_variable_name = "AZURE_STORAGE_SAS_TOKEN"
    elif target_container == "src":
        sas_token_variable_name = "SOURCE_CONTAINER_SAS_TOKEN"
    else:
        logger.error(
            f"Target container {target_container} must be one of ['dest', 'src']"
        )
        raise SystemExit(1)

    sas_token = os.getenv(sas_token_variable_name, None)

    if sas_token is not None:
        try:
            credential = AzureSasCredential(sas_token)
        except ClientAuthenticationError as e:
            logger.error(f"Encountered an issue when retrieving credentials: {e}")
            raise SystemExit(1)
    else:
        logger.error(f"Must set and export the {sas_token_variable_name} env variable")
        raise SystemExit(1)

    # Confirm that the SAS token is not expired
    expiry = re.search(
        r"se=([^&]*)Z",
        sas_token,
    )
    if expiry is None:
        logger.warning(
            "[WARN] Failed when checking if SAS token was expired; proceeding anyway"
        )
    else:
        expiry = datetime.fromisoformat(f"{unquote(expiry.group(1))}+00:00")
        if expiry < datetime.now(timezone.utc):
            logger.error(
                f"{sas_token_variable_name} is expired; please contact your administrator to get a new token."
            )
            raise SystemExit(1)

    return credential


def validate_bucket(blob_container):
    """
    Confirm that the target upload container exists

    Args:
        blob_container (str): Storage account, container, and optional path within container to upload data to; format <storage_account>/<container>[/<path_prefix>]

    Returns:
        formatted_container_url (str): Formatted container URL with paths stripped
        path_prefix (str): Path within the container to upload files to
    """
    storage_account = blob_container.split("/")[0]
    container_and_path = blob_container.split("/")[1:]
    formatted_container = container_and_path[0]
    path_prefix = (
        None if len(container_and_path) == 1 else "/".join(container_and_path[1:])
    )
    try:
        credential = _get_credential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential,
        )
        container_client = blob_service_client.get_container_client(formatted_container)

        # if we're able to list blobs, it means the container exists and is accessible
        next(container_client.list_blobs())
        logger.debug("\t✓ Target container exists and is accessible")
        return f"{storage_account}/{formatted_container}", path_prefix

    except StopIteration:
        # if we're able to list blobs but the container is empty, it's still accessible
        logger.debug("\t✓ Target container exists and is accessible")
        return f"{storage_account}/{formatted_container}", path_prefix

    except ClientAuthenticationError as e:
        logger.error(f"✗ Authentication failed: {e}")
        raise SystemExit(1)
    except ServiceRequestError as e:
        logger.error(f"✗ Azure configuration error: {e}")
        raise SystemExit(1)
    except ResourceNotFoundError:
        logger.error(
            f"\t✗ Target container {formatted_container} does not exist in storage account {storage_account}."
        )
        raise SystemExit(1)
    except Exception as e:
        logger.error(
            f"\t✗ Something went wrong when checking if the target container {blob_container} exists.\n\t{e}"
        )
        raise SystemExit(1)


def upload_sample_sync_file(raw_data_bucket, sample_sync_file_path):
    """
    Upload the sample sync file to the raw data bucket if it doesn't exist so that Samples are automatically registered in Workbench

    Args:
        raw_data_bucket (str): Storage account, container to upload data to; format <storage_account>/<container>
        sample_sync_file_path (str): Path to the (local) sample sync file to upload
    """
    expected_remote_path = (
        f"/{raw_data_bucket}/{os.path.basename(sample_sync_file_path)}"
    )

    file_exists, _, _, _ = check_file_exists(
        raw_data_bucket, None, expected_remote_path, None, None
    )
    if file_exists is False:
        upload_files(
            raw_data_bucket,
            {sample_sync_file_path: os.path.basename(sample_sync_file_path)},
        )


def check_file_exists(
    blob_container,
    path_prefix,
    file_path,
    sample_id,
    file_type,
):
    """
    Check if a file exists in the container; determine the expected path for remote files
    Args:
        blob_container (str): Storage account, container to upload data to; format <storage_account>/<container>
        path_prefix (str): Path within the container to upload files to
        file_path (str): Local path to the file
        sample_id (str): Unique identifier for sample
        file_type (str): File type (e.g., bam)

    Returns:
        file_exists (bool): True if the file exists at remote; False if it does not
        remote_path (str): Expected path to the file in target container
        file_size_bytes (int): If the file exists, the size of the file in bytes
        copy_status (str): ["pending", "success", None] - if the file was copied, what its status is
    """
    storage_account, container = blob_container.split("/")

    file_basename = os.path.basename(file_path)
    file_size_bytes = None
    copy_status = None

    # File is located in Azure Blob Storage and in the target container
    ## These files can be at different paths within the container than the expected one
    expected_prefix = f"/{storage_account}/{container}/"
    if file_path.startswith(expected_prefix):
        remote_path = file_path.removeprefix(expected_prefix)
    elif file_path.startswith(f"/{storage_account}/") and not file_path.startswith(
        expected_prefix
    ):
        logger.error(
            f"\t✗ Remote file path [{file_path}] is outside of the target container. Please download this file to local storage to allow it to be reuploaded to the target container."
        )
        raise SystemExit(1)
    # File is local; we'll upload to {path_prefix}/{sample_id}/{file_type}/{file_basename}
    else:
        remote_path = f"{path_prefix + '/' if path_prefix else ''}{sample_id}/{file_type}/{file_basename}"

    # Get the file's size if it exists
    try:
        credential = _get_credential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential,
        )
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=remote_path
        )
        object_metadata = blob_client.get_blob_properties()
        file_size_bytes = object_metadata["size"]
        copy_status = object_metadata["copy"]["status"]
        if copy_status == "pending":
            logger.debug(f"\t~ {file_basename} - pending")
            # not quite, but we won't reinitiate copy until it reaches a terminal state
            exists_at_remote = True
        elif copy_status in ["failed", "aborted", "invalid"]:
            logger.debug(f"\t✗ {file_basename} [previous copy failed - reinitiating]")
            # A previous copy failed, or something else has gone wrong
            exists_at_remote = False
        else:
            logger.debug(f"\t✓ {file_basename}")
            exists_at_remote = True
        return exists_at_remote, remote_path, file_size_bytes, copy_status
    except (ClientAuthenticationError, ServiceRequestError) as e:
        logger.error(f"✗ Azure configuration error: {e}")
        raise SystemExit(1)
    except ResourceNotFoundError:
        logger.debug(f"\t✗ {file_basename}")
        return False, remote_path, file_size_bytes, copy_status
    except Exception as e:
        logger.error(
            f"\t✗ Something went wrong when checking if the remote file {container}/{remote_path} in storage account {storage_account} exists.\n{e}"
        )
        raise SystemExit(1)


def check_file_exists_remote_src(file_path):
    """
    Check if a file exists in a remote src container
    Args:
        file_path (str): Path of the file in the remote src container

    Returns:
        file_exists (bool): True if the file exists at remote; False if it does not
        file_size_bytes (int): If the file exists, the size of the file in bytes
    """
    split_file_path = file_path.split("/")
    if len(split_file_path) < 4:
        logger.error(
            f"File path shorter than expected; should be in the format [/<storage_account>/<storage_container>/path/to/file.bam]. Got {file_path}"
        )
        raise SystemExit(1)

    storage_account = split_file_path[1]
    container = split_file_path[2]
    file_size_bytes = None

    remote_path = "/".join(split_file_path[3:])

    # Get the file's size if it exists
    try:
        credential = _get_credential(target_container="src")
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential,
        )
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=remote_path
        )
        object_metadata = blob_client.get_blob_properties()
        file_size_bytes = object_metadata["size"]
        return True, file_size_bytes
    except (ClientAuthenticationError, ServiceRequestError) as e:
        logger.error(f"✗ Azure configuration error: {e}")
        raise SystemExit(1)
    except ResourceNotFoundError:
        return False, file_size_bytes
    except Exception as e:
        logger.error(
            f"\t✗ Something went wrong when checking if the remote file {container}/{remote_path} in storage account {storage_account} exists.\n{e}"
        )
        raise SystemExit(1)


def transfer_files(dest_blob_container, files_to_transfer):
    """
    Transfer files from one Azure storage account to another

    Args:
        dest_blob_container (str): Storage account, container to upload data to; format <storage_account>/<container>
        files_to_transfer (dict): Dictionary of files to upload with keys=remote source path to the file (including the /<storage_account>/<container> prefix), values=destination remote path
    """
    if len(files_to_transfer) > 0:
        logger.info("Transferring files from src to target container")
        dest_storage_account, dest_container = dest_blob_container.split("/")

        # Confirm that there is only one source storage account, container
        src_blob_containers = list(
            set(
                [
                    "/".join(prefix.split("/")[1:3])
                    for prefix in files_to_transfer.keys()
                ]
            )
        )
        if len(src_blob_containers) > 1:
            logger.error(
                f"Expected a single source blob container; got {src_blob_containers}"
            )
            raise SystemExit(1)
        else:
            src_blob_container = src_blob_containers[0]

        src_storage_account, src_container = src_blob_container.split("/")

        dest_credential = _get_credential(target_container="dest")

        dest_service_client = BlobServiceClient(
            account_url=f"https://{dest_storage_account}.blob.core.windows.net",
            credential=dest_credential,
            max_single_put_size=4 * 1024 * 1024,
            connection_timeout=600,
        )

        src_sas_token = os.getenv("SOURCE_CONTAINER_SAS_TOKEN", None)
        if src_sas_token is None:
            logger.error(
                "Must define SOURCE_CONTAINER_SAS_TOKEN to transfer from Azure <> Azure"
            )
            raise SystemExit(1)

        for src_remote_path, dest_remote_path in files_to_transfer.items():
            src_blob_name = src_remote_path.removeprefix(f"/{src_blob_container}/")

            source_blob_url = f"https://{src_storage_account}.blob.core.windows.net/{src_container}/{src_blob_name}?{src_sas_token}"

            dest_blob_client = dest_service_client.get_blob_client(
                container=dest_container, blob=dest_remote_path
            )

            try:
                copy_props = dest_blob_client.start_copy_from_url(source_blob_url)
                logger.info(
                    f"\t~ {os.path.basename(src_blob_name)} - {copy_props['copy_status']}"
                )
            except ClientAuthenticationError:
                logger.error("Authentication failed; do src and dest containers exist?")
                raise SystemExit(1)
            except ResourceNotFoundError:
                logger.error(f"Failed to find remote src file {src_remote_path}")
                raise SystemExit(1)


def upload_files(blob_container, files_to_upload):
    """
    Upload files to the target container

    Args:
        blob_container (str): Storage account, container to upload data to; format <storage_account>/<container>
        files_to_upload (dict): Dictionary of files to upload with keys=local path to file, values=remote path
    """
    if len(files_to_upload) > 0:
        logger.info("Uploading files to target container")
        storage_account, container = blob_container.split("/")

        credential = _get_credential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential,
            max_single_put_size=4 * 1024 * 1024,
            connection_timeout=600,
        )
        container_client = blob_service_client.get_container_client(container)

        for local_path, remote_path in files_to_upload.items():
            try:
                blob_client = container_client.get_blob_client(remote_path)
                with open(local_path, "rb") as data:
                    blob_client.upload_blob(data)
                logger.debug(f"\t✓ {os.path.basename(local_path)}")
            except ClientAuthenticationError as e:
                logger.error(f"✗ Authentication failed: {e}")
                raise SystemExit(1)
            except ServiceRequestError as e:
                logger.error(f"✗ Azure configuration error: {e}")
                raise SystemExit(1)
            except ResourceNotFoundError:
                logger.error(
                    f"\t✗ Error uploading file {local_path}: The specified container {container} does not exist."
                )
                raise SystemExit(1)
            except Exception as e:
                logger.error(f"\t✗ Error uploading file {local_path}: {e}")
                raise SystemExit(1)


def get_static_workflow_inputs(
    reference_inputs_bucket,
    workflow_file_outputs_bucket,
    region=None,
    container_registry=None,
):
    """
    Generate the set of static workflow inputs

    Args:
        reference_inputs_bucket (str): Bucket where reference files are located
        workflow_file_outputs_bucket (str): Bucket where workflow output files will be written
        region (str): Region to run the workflow in; does not need to be specified when backend is Azure
        container_registry (str): Alternate container registry to pull workflow images from; defaults to [PacBio's public Quay.io](https://quay.io/organization/pacbio)

    Returns:
        static_inputs (dict): The set of static inputs for the workflow
    """
    reference_inputs_bucket = f"/{reference_inputs_bucket}"
    workflow_file_outputs_bucket = f"/{workflow_file_outputs_bucket}"

    static_inputs = {
        "HumanWGS_wrapper.ref_map_file": f"{reference_inputs_bucket}/dataset/map_files/GRCh38.ref_map.v2p0p0.azure.tsv",
        "HumanWGS_wrapper.backend": "Azure",
        "HumanWGS_wrapper.preemptible": True,
        "HumanWGS_wrapper.workflow_outputs_bucket": workflow_file_outputs_bucket,
    }

    if container_registry is not None:
        static_inputs["HumanWGS_wrapper.container_registry"] = container_registry

    return static_inputs


def generate_inputs_json(
    sample_info,
    reference_inputs_bucket,
    workflow_file_outputs_bucket,
    region=None,
    container_registry=None,
    **kwargs,
):
    """
    Generate the inputs JSON needed to execute a workflow run

    Args:
        sample_info (pd.DataFrame): Sample information
        reference_inputs_bucket (str): Bucket where reference files are located
        workflow_file_outputs_bucket (str): Bucket where workflow output files will be written
        region (str): Region to run the workflow in; does not need to be specified when backend is Azure
        container_registry (str): Alternate container registry to pull workflow images from; defaults to [PacBio's public Quay.io](https://quay.io/organization/pacbio)

    Returns:
        humanwgs_inputs (dict): Inputs JSON with all values filled out
        engine_params (dict): Configuration parameters for the engine
    """
    engine_params = {}

    samples = sample_info.drop(columns=["family_id", "total_file_size_bytes"]).to_dict(
        orient="records"
    )
    samples_no_null_values = [
        {
            key: value
            for key, value in sample.items()
            if isinstance(value, list) or pd.notnull(value)
        }
        for sample in samples
    ]

    family = {
        "family_id": sample_info["family_id"].unique()[0],
        "samples": samples_no_null_values,
    }

    humanwgs_inputs = {
        "HumanWGS_wrapper.family": family,
    }

    static_inputs = get_static_workflow_inputs(
        reference_inputs_bucket,
        workflow_file_outputs_bucket,
        region,
        container_registry,
    )

    humanwgs_inputs.update(static_inputs)

    return humanwgs_inputs, engine_params
