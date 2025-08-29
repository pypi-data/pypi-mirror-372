#!/usr/bin/env python3

from argparse import ArgumentParser

import importlib
import pkg_resources
import os
import pandas as pd
from pathlib import Path
import subprocess
import json
import hashlib
from .constants import (
    WORKBENCH_URL,
    WORKFLOW_NAME,
    WORKFLOW_VERSION,
    DERIVED_WORKFLOW_VERSION,
    AWS_CONTAINER_REGISTRY_ACCOUNT,
    WORKFLOW_PENDING_UPLOAD_STATE,
    WORKFLOW_UNSUBMITTED_STATE,
    WORKFLOW_RUNNING_STATE,
    WORKFLOW_SUCCEEDED_STATE,
    WORKFLOW_FAILED_STATE,
    WORKFLOW_STATE_SYMBOLS,
    WORKFLOW_STATES,
)
from .logger import setup_logger, logger

from importlib.metadata import version


def parse_args():
    """
    Parse command-line arguments

    Returns:
        args (argparse.Namespace): Parsed command-line arguments
    """
    parser = ArgumentParser(
        description="Upload genomics data and run PacBio's official Human WGS pipeline"
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version('hifi_solves_run_humanwgs')}; HumanWGS workflow {WORKFLOW_VERSION}, revision {DERIVED_WORKFLOW_VERSION}",
        help="Program version",
    )

    parser.add_argument(
        "--setup-only",
        required=False,
        action="store_true",
        help="Ensure the latest version of the workflow is registered in your Workbench account, then exit. Will not upload samples or trigger workflow runs.",
    )

    parser.add_argument(
        "--namespace",
        required=False,
        type=str,
        help="User namespace to use when running omics commands",
    )

    sample_info_group = parser.add_argument_group(
        "Sample information",
        "Provide either --sample-info, OR both --movie-bams and --fam-info",
    )
    sample_info_group.add_argument(
        "-s",
        "--sample-info",
        required=False,
        type=str,
        help="Path to sample info CSV or TSV. This file should have columns [family_id, sample_id, movie_bams, father_id, mother_id, sex]. See documentation for more information on the format of this file.",
    )
    sample_info_group.add_argument(
        "-m",
        "--movie-bams",
        required=False,
        type=str,
        help="Path to movie bams CSV or TSV. This file should have columns [sample_id, movie_bams]. Repeated rows for each sample can be added if the sample has more than one associated bam.",
    )

    sample_info_group.add_argument(
        "-c",
        "--fam-info",
        required=False,
        type=str,
        help="Path to family information. This file should have columns [family_id, sample_id, father_id, mother_id, sex]. It can optionally have additional phenotype columns (columns 6-end), but this information will not be used.",
    )

    parser.add_argument(
        "-b",
        "--backend",
        required=True,
        type=str.upper,
        help="Backend where infrastructure is set up",
        choices=["AWS", "GCP", "AZURE"],
    )

    parser.add_argument(
        "-r",
        "--region",
        required=True,
        type=str,
        help="Region where infrastructure is set up",
    )

    parser.add_argument(
        "-o",
        "--organization",
        required=True,
        type=str,
        help="Organization identifier; used to infer bucket names",
    )

    parser.add_argument(
        "-e",
        "--engine",
        required=False,
        type=str,
        help="Engine to use to run the workflow. Defaults to the default engine set in Workbench.",
    )

    parser.add_argument(
        "-u",
        "--upload-only",
        required=False,
        action="store_true",
        help="Upload BAMs and generate inputs JSON only; do not submit the workflow. If set, --write-inputs-json will also be set automatically.",
    )

    parser.add_argument(
        "-i",
        "--write-inputs-json",
        required=False,
        action="store_true",
        help="Write inputs JSON and engine configuration to a file. Files will be named {family_id}.inputs.json, {family_id}.engine_params.json, {family_id}.run_tags.json.",
    )

    parser.add_argument(
        "-f",
        "--force-rerun",
        "--force-rerun-failed",
        required=False,
        default=False,
        action="store_true",
        help="Force rerun samples that have previously been run and failed; will not rerun samples that are currently running or have a succeeded run.",
    )

    parser.add_argument(
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="Use verbose logging",
    )

    # AWS-specific
    parser.add_argument(
        "--aws-storage-capacity",
        required=False,
        type=str.upper,
        help="Storage capacity override for AWS HealthOmics backend. Defaults to total size of input BAMs across all samples * 8. Supply either the requested storage capacity in GB, or 'DYNAMIC' to set storage to dynamic.",
    )

    args = parser.parse_args()
    if args.setup_only is False:
        if args.sample_info is not None:
            if args.movie_bams is not None or args.fam_info is not None:
                parser.error(
                    "Either --sample-info alone, or both --movie-bams and --fam-info should be defined, not both.",
                )
        else:
            if args.movie_bams is None or args.fam_info is None:
                parser.error(
                    "If --sample-info is not defined, both --movie-bams and --fam-info must be set.",
                )

        if args.upload_only:
            args.write_inputs_json = True

        aws_storage_capacity = args.aws_storage_capacity
        if aws_storage_capacity is not None:
            if args.backend != "AWS":
                logger.warning(
                    "[WARN] --aws-storage-capacity argument ignored for non-AWS backend."
                )
            else:
                try:
                    args.aws_storage_capacity = int(aws_storage_capacity)
                except ValueError:
                    if args.aws_storage_capacity != "DYNAMIC":
                        parser.error(
                            "The value for --aws-storage-capacity must either by DYNAMIC or an integer representing the total storage capacity in GB."
                        )

    return args


def load_sample_info(sample_info_csv, movie_bams_csv, fam_file):
    """
    Load the sample info DataFrame, either from a single CSVs or a fam file and a CSV

    Args:
        sample_info_csv (str): Path to CSV containing all required sample information.
                               This file should have columns [family_id, sample_id, movie_bams, father_id, mother_id, sex]. If the file has the phenotypes column, it will be dropped.
        movie_bams_csv (str): Path to a file relating samples to their corresponding set of BAM files
        fam_file (str): Path to a FAM info file. See [here](https://www.cog-genomics.org/plink/2.0/formats#fam) for format. Note that multiple phenotype columns may be added. All phenotypes will be dropped.

    Returns:
        sample_info (pd.DataFrame): DataFrame containing sample information
    """
    if sample_info_csv is not None:
        sample_info = pd.read_csv(
            sample_info_csv,
            sep=None,
            engine="python",
            dtype={
                "family_id": str,
                "sample_id": str,
                "movie_bams": str,
                "phenotypes": str,
                "father_id": str,
                "mother_id": str,
                "sex": str,
            },
        )
        if "phenotypes" in sample_info.columns:
            sample_info = sample_info.drop(columns="phenotypes")

        sample_info.columns = (
            sample_info.columns.str.strip().str.lower().str.replace(" ", "_")
        )
    else:
        movie_bams = pd.read_csv(
            movie_bams_csv,
            sep=None,
            engine="python",
            dtype={"sample_id": str, "movie_bams": str},
        )
        movie_bams.columns = (
            movie_bams.columns.str.strip().str.lower().str.replace(" ", "_")
        )
        fam = pd.read_csv(fam_file, sep=None, engine="python")
        # drop anything after the 5th column (phenotypes)
        fam = fam.iloc[:, :5]
        fam.columns = fam.columns.str.strip()
        fam_columns = fam.columns.tolist()

        fam.columns = [col.lower().replace(" ", "_") for col in fam_columns]
        fam = fam.rename(
            columns={
                "fid": "family_id",
                "iid": "sample_id",
                "fatheriid": "father_id",
                "father_iid": "father_id",
                "f_iid": "father_id",
                "motheriid": "mother_id",
                "mother_iid": "mother_id",
                "m_iid": "mother_id",
            }
        )

        sample_info = pd.merge(movie_bams, fam, on="sample_id", how="outer")

    # Strip whitespace from values
    sample_info = sample_info.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )

    return sample_info


def import_backend_module(backend):
    """
    Import backend-specific functions

    Args:
        backend (str): Backend where infrastructure is set up ["AWS", "GCP", "AZURE"]

    Returns:
        (module): Module containing backend-specific functions
    """
    try:
        backend_module = importlib.import_module(
            f".backends.{backend.lower()}", package="hifi_solves_run_humanwgs"
        )
    except ModuleNotFoundError as e:
        if f"backends.{backend.lower()}" in str(e):
            logger.error(f"✗ Module backends.{backend.lower()} not found.")
            raise SystemExit(1)
        else:
            raise
    except ImportError as e:
        logger.error(f"✗ Import error in backends.{backend.lower()}")
        raise SystemExit(1)
    except Exception as e:
        logger.error(
            f"✗ Something went wrong when attempting to import the backend module\n{e}"
        )
        raise SystemExit(1)

    return backend_module


def _confirm_unique_values(sample_info, columns):
    """
    Confirm that there is exactly one unique value for each family_id/sample_id combination for a set of columns in the DataFrame

    Args:
        sample_info (pd.DataFrame): DataFrame containing sample information
        columns (List[str]): Set of columns to check

    Raises:
        ValueError: If there is more than one unique value for any combination of family_id, sample_id
    """
    sample_info = sample_info.set_index(["family_id", "sample_id"])
    for column in columns:
        unique_values = sample_info.groupby(["family_id", "sample_id"])[
            column
        ].nunique()
        if (unique_values > 1).any():
            problematic_samples = sample_info[
                sample_info.index.isin(unique_values[unique_values > 1].index)
            ]
            logger.error(
                f"\t✗ There should be exactly one unique value of {column} for each combination of family_id, sample_id\n{problematic_samples}"
            )
            raise SystemExit(1)


def _standardize_sex(sample_info):
    """
    Standardize the representation of sex in the sample_info DataFrame

    Args:
        sample_info (pd.DataFrame): DataFrame containing sample information

    Returns:
        sample_info (pd.DataFrame): DataFrame containing sample information with sex standardized
    """
    sex_mapping = {
        "MALE": "MALE",
        "M": "MALE",
        "1": "MALE",
        "FEMALE": "FEMALE",
        "F": "FEMALE",
        "2": "FEMALE",
        "None": None,
        "UNKNOWN": None,
        "0": None,
        "-1": None,
        "Null": None,
    }

    def map_sex(value):
        if pd.isna(value):
            return None
        elif str(value).upper() in sex_mapping:
            return sex_mapping[str(value).upper()]
        else:
            raise KeyError(
                f"Invalid sex '{value}'; should be one of ['MALE', 'FEMALE', None (empty value)]"
            )

    sample_info["sex"] = sample_info["sex"].map(map_sex)

    return sample_info


def check_missing_parent(row, valid_samples):
    """
    Check whether a given mother or father is found in the same family

    Args:
        row (pd.Series): Info for a particular sample; at minimum, fields family_id, sample_id, mother_id, and father_id must be present
        valid_samples (set): The set of (family_id, sample_id) tuples that exist in sample_info; used to check whether a given mother or father ID has a matching family_id

    Returns:
        is_valid_parent (bool): True if any non-None mother and father IDs for a given sample are present in sample_info and have the same family ID as that sample
    """
    # check mother
    if (
        pd.notna(row["mother_id"])
        and (row["family_id"], row["mother_id"]) not in valid_samples
    ):
        return False

    if (
        pd.notna(row["father_id"])
        and (row["family_id"], row["father_id"]) not in valid_samples
    ):
        return False

    return True


def validate_format_sample_info(sample_info):
    """
    Validate that sample_info contains the required information and reformat it

    Args:
        sample_info (pd.DataFrame): DataFrame containing sample information

    Returns:
        formatted_sample_info (pd.DataFrame): Reformatted and validated sample information
    """
    required_columns = ["family_id", "sample_id", "movie_bams"]
    optional_columns = ["father_id", "mother_id", "sex"]

    # Confirm all the required columns are present
    missing_required_columns = set(required_columns) - set(sample_info.columns)
    if missing_required_columns:
        logger.error(
            f"\t✗ Missing required columns: {', '.join(sorted(missing_required_columns))}"
        )
        raise SystemExit(1)
    for col in optional_columns:
        if col not in sample_info.columns:
            sample_info[col] = None

    sample_info = _standardize_sex(sample_info)

    # Confirm that there is exactly one unique value of mother_id, father_id, sex for each combination of family_id, sample_id
    _confirm_unique_values(sample_info, ["mother_id", "father_id", "sex"])

    # Gather the set of movie_bams for each family_id-sample_id combination
    sample_info = (
        sample_info.groupby(["family_id", "sample_id"])
        .agg(
            {
                "movie_bams": lambda x: (
                    (sorted(list(set(x.dropna())))) if x.notnull().any() else None
                ),
                "father_id": "first",
                "mother_id": "first",
                "sex": "first",
            }
        )
        .reset_index()
    )

    # Confirm that there are no null values in any required column
    na_values = sample_info[required_columns].isna().any()
    if na_values.any():
        missing_value_columns = na_values[na_values].index.tolist()
        logger.error(
            f"\t✗ Missing values found in required columns: {', '.join(missing_value_columns)}"
        )
        raise SystemExit(1)

    # Confirm that there are no duplicate bams across different samples
    movie_bams = sample_info["movie_bams"].explode().dropna()
    if len(movie_bams) != len(set(movie_bams)):
        seen_bams = set()
        duplicate_bams = set()
        for movie_bam in movie_bams:
            if movie_bam in seen_bams:
                duplicate_bams.add(movie_bam)
            else:
                seen_bams.add(movie_bam)
        logger.error(f"\t✗ Duplicate movie bams found: {', '.join(duplicate_bams)}")
        raise SystemExit(1)

    # Confirm that the same sample is not found in different family_ids
    duplicate_samples = sample_info.groupby("sample_id")["family_id"].nunique()
    duplicate_samples = duplicate_samples[duplicate_samples > 1]
    if not duplicate_samples.empty:
        logger.error(
            f"\t✗ The same sample was found under multiple family IDs; please ensure sample_ids are unique. Problematic samples: \n{list(duplicate_samples.index)}"
        )
        raise SystemExit(1)

    # If father_id or mother_id is set, confirm that there is a sample with that ID in the family
    samples_with_parent_set = sample_info.dropna(
        subset=["father_id", "mother_id"], how="all"
    )
    valid_samples = set(zip(sample_info["family_id"], sample_info["sample_id"]))
    invalid_samples = samples_with_parent_set[
        ~samples_with_parent_set.apply(
            check_missing_parent, axis=1, args=(valid_samples,)
        )
    ]
    if not invalid_samples.empty:
        logger.error(
            f"\t✗ Mother or father ID for samples given were either not found in the cohort, or have a different family_id\n{invalid_samples}"
        )
        raise SystemExit(1)

    # Rename movie_bams to hifi_reads for input JSON creation
    sample_info = sample_info.rename(columns={"movie_bams": "hifi_reads"})

    sample_info.set_index("sample_id", drop=False, inplace=True)

    # Set affected status to false for every sample
    sample_info["affected"] = False

    return sample_info


def _check_file_exists_locally(file_path):
    """
    Check if a file exists locally

    Args:
        file_path (str): Path to file

    Returns:
        file_exists (bool): True if file exists at path; False if it does not
        file_size_bytes (int): If the file exists, the size of the file in bytes
    """
    file_exists = Path(file_path).exists()
    file_size_bytes = None
    if file_exists:
        file_size_bytes = Path(file_path).stat().st_size

    return file_exists, file_size_bytes


def upload_files(
    sample_info,
    backend_module,
    raw_data_bucket,
    backend,
    path_prefix=None,
):
    """
    Check whether files exist in the raw_data_bucket; if not, upload them

    Args:
        sample_info (pd.DataFrame): Sample information
        backend_module (module): Module containing backend-specific functions
        raw_data_bucket (str): Bucket where workflow input files will be uploaded
        backend (str): Backend where infrastructure is set up ["AWS", "GCP", "AZURE"]
        path_prefix (str): Path within the bucket to upload files to

    Returns:
        formatted_sample_info (pd.DataFrame): Sample information with bams paths
            translated to their remote equivalent
        pending_families (np.ndarray): List of families that have any files pending transfer
    """
    logger.info("Checking whether files exist in the target bucket")
    file_info = {}
    sample_file_size_bytes = {}
    pending_samples = []
    for sample_id, file_path in sample_info["hifi_reads"].explode().items():
        exists_locally, local_size_bytes = _check_file_exists_locally(file_path)

        exists_at_remote, remote_path, remote_size_bytes, copy_status = (
            backend_module.check_file_exists(
                raw_data_bucket, path_prefix, file_path, sample_id, "bam"
            )
        )

        # if we can't find the file locally or at the remote, check if it's in a src_remote (ie a cloud bucket that is not the dest)
        # TODO only Azure -> Azure remote -> remote is supported at present
        if backend == "AZURE" and exists_locally is False and exists_at_remote is False:
            exists_at_src_remote, src_remote_size_bytes = (
                backend_module.check_file_exists_remote_src(file_path)
            )
            if exists_at_src_remote is True and src_remote_size_bytes == 0:
                raise SystemExit(
                    f"Requested input file {file_path} has a size of 0 bytes; please verify file health and try again"
                )
        else:
            exists_at_src_remote = False
            src_remote_size_bytes = None

        file_size_bytes = next(
            (
                size
                for size in [remote_size_bytes, local_size_bytes, src_remote_size_bytes]
                if size is not None
            ),
            None,
        )

        if file_size_bytes is not None:
            if sample_id in sample_file_size_bytes:
                sample_file_size_bytes[sample_id] += file_size_bytes
            else:
                sample_file_size_bytes[sample_id] = file_size_bytes
        else:
            logger.error(f"Failed to retrieve file size for file {file_path}; exiting")
            raise SystemExit(1)

        file_info[file_path] = {
            "exists_locally": exists_locally,
            "exists_at_remote": exists_at_remote,
            "exists_at_src_remote": exists_at_src_remote,
            "remote_path": remote_path,
            "file_size_bytes": file_size_bytes,
        }

        # pending_samples = samples we've previously initiated copy for that have not completed, or samples we're about to initiate copy for
        # includes samples that previously failed to copy which, for which we will reinitiate transfer
        if sample_id not in pending_samples and (
            (copy_status is not None and copy_status != "success")
            or (exists_at_src_remote is True and exists_at_remote is False)
        ):
            pending_samples.append(sample_id)

    # Error if any files do not exist locally or at remote
    files_not_found = [
        k
        for k, v in file_info.items()
        if not v["exists_locally"]
        and not v["exists_at_src_remote"]
        and not v["exists_at_remote"]
    ]
    if len(files_not_found) > 0:
        logger.error(
            f"\t✗ Some files were not found locally, in the destination data bucket [{raw_data_bucket}], or in at a different remote source. Check paths? Files with issues:\n{files_not_found}"
        )
        raise SystemExit(1)

    # Upload files that are local to the remote; if they exist at a src_remote, prefer transferring them cloud <> cloud
    files_to_upload = {
        k: v["remote_path"]
        for k, v in file_info.items()
        if v["exists_locally"]
        and not v["exists_at_remote"]
        and not v["exists_at_src_remote"]
    }
    backend_module.upload_files(raw_data_bucket, files_to_upload)

    # Transfer files from src remote -> remote
    # TODO N.B. only works for Azure at present
    if backend == "AZURE":
        files_to_transfer = {
            k: v["remote_path"]
            for k, v in file_info.items()
            if v["exists_at_src_remote"] and not v["exists_at_remote"]
        }
        backend_module.transfer_files(raw_data_bucket, files_to_transfer)

    # Remove families where any sample in that family has files pending copy
    pending_families = sample_info[sample_info["sample_id"].isin(pending_samples)][
        "family_id"
    ].unique()
    sample_info = sample_info[~sample_info["family_id"].isin(pending_families)].copy()

    sample_info["total_file_size_bytes"] = sample_info["sample_id"].map(
        sample_file_size_bytes
    )

    # Define cloud-specific prefixes
    if backend == "AWS":
        prefix = "s3://"
    elif backend == "AZURE":
        prefix = "/"
    elif backend == "GCP":
        prefix = "gs://"

    sample_info["hifi_reads"] = sample_info["hifi_reads"].apply(
        lambda x: [
            (f"{prefix}{raw_data_bucket}/{file_info[hifi_read]['remote_path']}")
            for hifi_read in x
        ]
    )

    return sample_info, pending_families


def _register_or_retrieve_workflow(workflow_name, workflow_version, namespace):
    """
    Register or retrieve a workflow from Workbench

    Args:
        workflow_name (str): Name of the workflow
        workflow_version (str): Workflow version
        namespace (str): Optional namespace to use; by default, will be derived from the user's context

    Returns:
        workflow_id (str): Workflow ID for the workflow
    """

    def _register_workflow(workflow_name, workflow_version):
        package_path = pkg_resources.resource_filename("hifi_solves_run_humanwgs", "")
        entrypoint_path = os.path.join(
            package_path, "workflows", "hifisolves_wrapper.wdl"
        )

        create_wf_args = [
            "omics",
            "workbench",
            "workflows",
            "create",
            "--name",
            workflow_name,
            "--version-name",
            workflow_version,
            "--entrypoint",
            entrypoint_path,
        ]

        if namespace is not None:
            create_wf_args += ["--namespace", namespace]

        workflow_info = subprocess.run(
            create_wf_args,
            capture_output=True,
            text=True,
        )
        if workflow_info.returncode == 0:
            try:
                workflow_info_json = json.loads(workflow_info.stdout)
                workflow_id = workflow_info_json["internalId"]
                logger.debug("\t✓ Registered workflow")
                return workflow_id
            except json.JSONDecodeError as e:
                logger.error(f"\t✗ Error parsing JSON: {e}")
                raise SystemExit(1)
        else:
            logger.error(
                f"\t✗ Something went wrong when attempting to register the workflow\n{workflow_info.stderr}"
            )
            raise SystemExit(1)

    # See if the workflow exists
    list_wf_args = [
        "omics",
        "workbench",
        "workflows",
        "list",
        "--source",
        "PRIVATE",
        "--search",
        workflow_name,
    ]

    if namespace is not None:
        list_wf_args += ["--namespace", namespace]

    workflow_list = subprocess.run(
        list_wf_args,
        capture_output=True,
        text=True,
    )

    if workflow_list.returncode == 0:
        try:
            workflow_list_json = json.loads(workflow_list.stdout)
            filtered_workflow_list = [
                workflow
                for workflow in workflow_list_json
                if workflow["name"] == workflow_name
            ]
            if len(filtered_workflow_list) > 0:
                workflow_id = filtered_workflow_list[0]["internalId"]
            else:
                logger.debug("\tWorkflow not found in Workbench; registering workflow")
                workflow_id = _register_workflow(workflow_name, workflow_version)
        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}\n{workflow_list.stderr}")
            raise SystemExit(1)
    else:
        logger.error(
            f"\t✗ Something went wrong when listing workflows\n{workflow_list.stderr}"
        )
        raise SystemExit(1)

    return workflow_id


def _register_workflow_version(workflow_id, workflow_version, namespace):
    """
    Register a workflow version in Workbench, if it does not already exist

    Args:
        workflow_id (str): The ID of the workflow registered in Workbench to version
        workflow_version (str): The verison of the workflow to register
        namespace (str): Optional namespace to use; by default, will be derived from the user's context
    """

    def _register_version(workflow_id, workflow_version):
        package_path = pkg_resources.resource_filename("hifi_solves_run_humanwgs", "")
        entrypoint_path = os.path.join(
            package_path, "workflows", "hifisolves_wrapper.wdl"
        )

        register_version_args = [
            "omics",
            "workbench",
            "workflows",
            "versions",
            "create",
            "--workflow",
            workflow_id,
            "--name",
            workflow_version,
            "--entrypoint",
            entrypoint_path,
        ]

        if namespace is not None:
            register_version_args += ["--namespace", namespace]

        version_info = subprocess.run(
            register_version_args,
            capture_output=True,
            text=True,
        )

        if version_info.returncode == 0:
            logger.debug("\t✓ Registered workflow version")
        else:
            logger.error(
                f"\t✗ Something went wrong when attempting to register a workflow version\n{version_info.stderr}"
            )
            raise SystemExit(1)

    # See if the workflow version exists
    list_versions_args = [
        "omics",
        "workbench",
        "workflows",
        "versions",
        "list",
        "--workflow",
        workflow_id,
    ]

    if namespace is not None:
        list_versions_args += ["--namespace", namespace]

    versions_list = subprocess.run(
        list_versions_args,
        capture_output=True,
        text=True,
    )

    if versions_list.returncode == 0:
        try:
            versions_list_json = json.loads(versions_list.stdout)
            all_versions = [v["id"] for v in versions_list_json]
            if workflow_version not in all_versions:
                _register_version(workflow_id, workflow_version)
        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}\n{versions_list.stderr}")
            raise SystemExit(1)
    else:
        logger.error(
            f"\t✗ Something went wrong when listing workflow versions\n{versions_list.stderr}"
        )
        raise SystemExit(1)


def _register_workflow_defaults(
    workflow_id, workflow_version, backend, region, static_inputs, namespace
):
    """
    Define the default (static) values for the workflow inputs, if they don't exist

    Args:
        workflow_id (str): The ID of the workflow registered in Workbench to version
        workflow_version (str): The verison of the workflow to register
        backend (str): The cloud backend where infrastructure will be run; used as a selector for defaults values
        region (str): The cloud region where infrastructure will be run; used a a selector for defaults values
        static_inputs (dict): The set of static inputs for the workflow
        namespace (str): Optional namespace to use; by default, will be derived from the user's context
    """

    def _get_default_set_by_selector(defaults_list_json, selector):
        for default_set in defaults_list_json:
            if default_set["selector"] == selector:
                return default_set
        return None

    def _register_defaults(
        workflow_id,
        workflow_version,
        backend,
        region,
        defaults_version_id,
        values,
        update=False,
    ):
        if update is True:
            defaults_cmd = "update"
        else:
            defaults_cmd = "create"

        crud_defaults_args = [
            "omics",
            "workbench",
            "workflows",
            "versions",
            "defaults",
            defaults_cmd,
            "--workflow",
            workflow_id,
            "--version",
            workflow_version,
            "--provider",
            backend,
            "--region",
            region,
            "--values",
            json.dumps(values),
            defaults_version_id,
        ]

        if namespace is not None:
            crud_defaults_args += ["--namespace", namespace]

        default_info = subprocess.run(
            crud_defaults_args,
            capture_output=True,
            text=True,
        )

        if default_info.returncode == 0:
            logger.debug("\t✓ Registered workflow defaults")
        else:
            logger.error(
                f"\t✗ Something went wrong when attempting to register workflow defaults\n{default_info.stderr}"
            )
            raise SystemExit(1)

    selector = {"engine": None, "provider": backend, "region": region}

    # Check if workflow defaults already exist and match the defaults we're trying to set
    # If not, register them
    list_defaults_args = [
        "omics",
        "workbench",
        "workflows",
        "versions",
        "defaults",
        "list",
        "--workflow",
        workflow_id,
        "--version",
        workflow_version,
    ]

    if namespace is not None:
        list_defaults_args += ["--namespace", namespace]

    defaults_list = subprocess.run(
        list_defaults_args,
        capture_output=True,
        text=True,
    )

    if defaults_list.returncode == 0:
        try:
            defaults_list_json = json.loads(defaults_list.stdout)

            existing_default_set = _get_default_set_by_selector(
                defaults_list_json, selector
            )
            if existing_default_set is None:
                # We'll just use the workflow version as the defaults version ID (but no periods allowed)
                # Using backend and region as part of the ID means you can configure different defaults for different engine setups
                defaults_version_id = (
                    f"{workflow_version.replace('.', '_')}_{backend}_{region}"
                )
                _register_defaults(
                    workflow_id,
                    workflow_version,
                    backend,
                    region,
                    defaults_version_id,
                    static_inputs,
                    update=False,
                )
            else:
                # The existing default already has the correct values
                if existing_default_set["values"] == static_inputs:
                    return
                else:
                    # The existing default has different values; update it
                    _register_defaults(
                        workflow_id,
                        workflow_version,
                        backend,
                        region,
                        existing_default_set["id"],
                        static_inputs,
                        update=True,
                    )

        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}\n{defaults_list.stderr}")
            raise SystemExit(1)
    else:
        logger.error(
            f"\t✗ Something went wrong when listing workflow defaults versions\n{defaults_list.stderr}"
        )
        raise SystemExit(1)


def _register_workflow_transformations(workflow_id, workflow_version, namespace):
    """
    Define the transformations needed to map samples into workflow inputs, if they don't exist

    Args:
        workflow_id (str): The ID of the workflow registered in Workbench to version
        workflow_version (str): The verison of the workflow to register
        namespace (str): Optional namespace to use; by default, will be derived from the user's context
    """

    def _register_transformation(
        workflow_id,
        workflow_version,
        transformation_js,
        transformation_id,
        existing_transformation_id=None,
    ):
        if existing_transformation_id is not None:
            # delete the existing transformation
            delete_transformation_args = [
                "omics",
                "workbench",
                "workflows",
                "versions",
                "transformations",
                "delete",
                "-f",
                "--workflow",
                workflow_id,
                "--version",
                workflow_version,
                existing_transformation_id,
            ]

            if namespace is not None:
                delete_transformation_args += ["--namespace", namespace]

            transformation_deleted_info = subprocess.run(
                delete_transformation_args,
                capture_output=True,
                text=True,
            )

            if transformation_deleted_info.returncode != 0:
                logger.error(
                    f"\t✗ Something went wrong when attempting to delete an existing workflow transformation\n{transformation_deleted_info.stderr}"
                )
                raise SystemExit(1)

        create_transformation_args = [
            "omics",
            "workbench",
            "workflows",
            "versions",
            "transformations",
            "create",
            "--workflow",
            workflow_id,
            "--version",
            workflow_version,
            "--label",
            "samples",
            "--label",
            "family",
            "--label",
            "hifisolves-ingest",
            "--id",
            transformation_id,
            f"{transformation_js}",
        ]

        if namespace is not None:
            create_transformation_args += ["--namespace", namespace]

        transformation_info = subprocess.run(
            create_transformation_args,
            capture_output=True,
            text=True,
        )

        if transformation_info.returncode == 0:
            logger.debug("\t✓ Registered workflow transformation")
        else:
            logger.error(
                f"\t✗ Something went wrong when attempting to register a workflow transformation\n{transformation_info.stderr}"
            )
            raise SystemExit(1)

    package_path = pkg_resources.resource_filename("hifi_solves_run_humanwgs", "")
    transformation_path = os.path.join(package_path, "instruments", "transformation.js")
    with open(transformation_path, "r") as f:
        transformation_js = f.read()

    # See if the workflow transformation exists
    list_transformations_args = [
        "omics",
        "workbench",
        "workflows",
        "versions",
        "transformations",
        "list",
        "--workflow",
        workflow_id,
        "--version",
        workflow_version,
    ]

    if namespace is not None:
        list_transformations_args += ["--namespace", namespace]

    transformations_list = subprocess.run(
        list_transformations_args,
        capture_output=True,
        text=True,
    )

    if transformations_list.returncode == 0:
        try:
            transformations_list_json = json.loads(transformations_list.stdout)
            n_transformations = len(transformations_list_json)

            # We'll just use the workflow version as the transformation ID (but no periods allowed)
            transformation_id = workflow_version.replace(".", "_")

            # unlikely to actually have more than 1 transformation, but let's confirm that
            if n_transformations == 0:
                # register a new transformation
                _register_transformation(
                    workflow_id,
                    workflow_version,
                    transformation_js,
                    transformation_id,
                )
            elif n_transformations == 1:
                # confirm that the transformation contents hasn't changed; update it if it has
                if transformations_list_json[0]["script"] == transformation_js:
                    return
                else:
                    # update the transformation
                    _register_transformation(
                        workflow_id,
                        workflow_version,
                        transformation_js,
                        transformation_id,
                        transformations_list_json[0]["id"],
                    )
            else:
                logger.error(
                    f"Expected exactly one transformation for the workflow; got {n_transformations}"
                )
                raise SystemExit(1)

        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}\n{transformations_list.stderr}")
            raise SystemExit(1)

    else:
        logger.error(
            f"\t✗ Something went wrong when listing workflow transformations\n{_register_transformation.stderr}"
        )
        raise SystemExit(1)


def configure_workflow(
    workflow_name, workflow_version, backend, region, static_inputs, namespace
):
    """
    Register and configure the HumanWGS workflow if it does not exist; get the workflow_id if it does

    Args:
        workflow_name (str): Name of the workflow
        workflow_version (str): Workflow version
        backend (str): The cloud backend where infrastructure will be run; used as a selector for defaults values
        region (str): The cloud region where infrastructure will be run; used as a selector for defaults values
        static_inputs (dict): The set of static inputs for the workflow
        namespace (str): Optional namespace to use; by default, will be derived from the user's context

    Returns:
        workflow_id (str): Workflow ID for the HumanWGS wrapper workflow
    """
    workflow_id = _register_or_retrieve_workflow(
        workflow_name, workflow_version, namespace
    )
    _register_workflow_version(workflow_id, workflow_version, namespace)
    _register_workflow_defaults(
        workflow_id, workflow_version, backend, region, static_inputs, namespace
    )
    _register_workflow_transformations(workflow_id, workflow_version, namespace)

    return workflow_id


def write_inputs_json(
    family_id, workflow_inputs, engine_params, tags, inputs_dir="inputs"
):
    """
    Write inputs JSON (and engine_params, if any) to files

    Args:
        family_id (str): Unique family ID for the run
        workflow_inputs (dict): Inputs JSON that will be used to trigger the workflow
        engine_params (dict): Configuration parameters for the engine
        tags (dict): Set of tags to add to the workflow run
    """
    fam_inputs_dir = f"{inputs_dir}/{family_id}"
    os.makedirs(fam_inputs_dir, exist_ok=True)

    inputs_json_file = f"{fam_inputs_dir}/{family_id}.inputs.json"
    engine_params_file = f"{fam_inputs_dir}/{family_id}.engine_params.json"
    tags_file = f"{fam_inputs_dir}/{family_id}.run_tags.json"

    logger.debug(f"Writing workflow inputs")

    # Write inputs JSON
    if os.path.exists(inputs_json_file):
        with open(inputs_json_file, "r") as f:
            existing_inputs = json.load(f)

        if workflow_inputs == existing_inputs:
            logger.warning(
                f"\t✓ Existing identical inputs file found; continuing [{inputs_json_file}]"
            )
        else:
            logger.error(
                f"\t✗ Inputs JSON file [{inputs_json_file}] already exists and has different contents to the current inputs; won't overwrite!\n\tEither delete this file, or use a unique family identifier in the sample information file."
            )
            raise SystemExit(1)
    else:
        with open(inputs_json_file, "w") as f:
            json.dump(workflow_inputs, f, indent=2)
        logger.debug(f"\t✓ Wrote inputs to {inputs_json_file}")

    # Write engine params
    with open(engine_params_file, "w") as f:
        json.dump(engine_params, f, indent=2)
    logger.debug(f"\t✓ Wrote engine params to {engine_params_file}")

    # Write run tags
    with open(tags_file, "w") as f:
        json.dump(tags, f, indent=2)
    logger.debug(f"\t✓ Wrote run tags to {tags_file}")


def get_tags(workflow_inputs):
    """
    Get tags for a workflow run

    Args:
        workflow_inputs (dict): Inputs JSON that will be used to trigger the workflow

    Returns:
        tags (dict): Set of tags to add to the workflow run
    """
    samples = "/".join(
        [
            sample["sample_id"]
            for sample in workflow_inputs["HumanWGS_wrapper.family"]["samples"]
        ]
    )

    # Note that the same inputs run in different clouds will have different input hashes, because the inputs include the path to the files (cloud-specific)
    inputs_hash = hashlib.md5(
        (json.dumps(workflow_inputs, sort_keys=True)).encode("utf-8")
    ).hexdigest()

    tags = {
        "family_id": workflow_inputs["HumanWGS_wrapper.family"]["family_id"],
        "samples": samples,
        "inputs_hash": inputs_hash,
    }

    return tags


def list_previous_runs(tags, workflow_id, workflow_version):
    """
    Get the list of previous runs using the same set of tags that this input set / workflow version would produce - includes ALL runs (including failed)

    Args:
        tags (dict): Set of tags added to the workflow run; must include inputs_hash
        workflow_id (str): The workflow ID of the workflow registered in Workbench
        workflow_version (str): The version of the workflow to submit; will match anything with the same workflow version (humanWGS version) and the same workflow_sub_version (revision) major version

    Returns:
        runs (dict): Set of runs that contains all of the given tags
    """
    # Only force reruns if the WORKFLOW_SUB_VERSION major version has changed (or if any part of the workflow main version has changed)
    if "_" in workflow_version:
        main_version, sub_version = workflow_version.split("_", 1)
        # Extract major version from sub-version (e.g., "v0.0.1" -> "v0.")
        if sub_version.startswith("v") and "." in sub_version[1:]:
            sub_major = sub_version.split(".")[0] + "."
            search_pattern = f"{workflow_id}/versions/{main_version}_{sub_major}"
        else:
            # Fallback to exact version match if format is unexpected
            search_pattern = f"{workflow_id}/versions/{workflow_version}"
    else:
        search_pattern = f"{workflow_id}/versions/{workflow_version}"

    run_list = subprocess.run(
        [
            "omics",
            "workbench",
            "runs",
            "list",
            "--tags",
            json.dumps({"inputs_hash": tags["inputs_hash"]}),
            "--search",
            search_pattern,
        ],
        capture_output=True,
        text=True,
    )
    if run_list.returncode == 0:
        try:
            run_list_json = json.loads(run_list.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}")
            raise SystemExit(1)
    else:
        logger.error(
            f"\t✗ Something went wrong when listing previous runs\n{run_list.stderr}"
        )
        raise SystemExit(1)

    return run_list_json


def trigger_workflow_run(
    family_id,
    workflow_inputs,
    workflow_id,
    workflow_version,
    engine,
    engine_params,
    tags,
    rerun=False,
):
    """
    Trigger a run of the workflow via Workbench

    Args:
        family_id (str): Family ID for the run being submitted
        workflow_inputs (dict): Inputs JSON that will be used to trigger the workflow
        workflow_id (str): The workflow ID of the workflow registered in Workbench
        workflow_version (str): The version of the workflow to submit
        engine (str): Engine ID to run the workflow through; defaults to the default engine configured in Workbench
        engine_params (dict): Configuration parameters for the engine
        tags (dict): Set of tags to add to the workflow run
        rerun (bool): Whether or not to force rerun samples that have already been run

    Returns:
        family_run_state (str): ["UNSUBMITTED", "RUNNING", "SUCCEEDED", "FAILED"]
    """
    # Ensure this combination of workflow/version/inputs has not been run before (successful or failed)
    previous_runs = list_previous_runs(tags, workflow_id, workflow_version)
    family_run_state = WORKFLOW_UNSUBMITTED_STATE
    if len(previous_runs) > 0:
        run_states = {WORKFLOW_STATES[run["state"]] for run in previous_runs}
        if WORKFLOW_SUCCEEDED_STATE in run_states:
            family_run_state = WORKFLOW_SUCCEEDED_STATE
        elif WORKFLOW_RUNNING_STATE in run_states:
            family_run_state = WORKFLOW_RUNNING_STATE
        elif WORKFLOW_FAILED_STATE in run_states:
            family_run_state = WORKFLOW_FAILED_STATE
        else:
            raise SystemExit(
                f"Not sure how we got here, but run_states are {run_states}"
            )

        workflow_state_symbol = WORKFLOW_STATE_SYMBOLS[family_run_state]

        if rerun is False:
            logger.debug(f"\t{workflow_state_symbol} {family_id}")
            return family_run_state
        else:
            if family_run_state in [WORKFLOW_RUNNING_STATE, WORKFLOW_SUCCEEDED_STATE]:
                logger.debug(f"\t{workflow_state_symbol} {family_id}")
                return family_run_state
            else:
                logger.info(f"\tForce-rerunning failed family {family_id}")

    workflow_run_cmd = [
        "omics",
        "workbench",
        "runs",
        "submit",
        "--url",
        f"{workflow_id}/{workflow_version}",
        "--workflow-params",
        json.dumps(workflow_inputs),
        "--tags",
        json.dumps(tags),
    ]
    if len(engine_params) > 0:
        engine_params_string = ",".join([f"{k}={v}" for k, v in engine_params.items()])
        workflow_run_cmd.extend(
            [
                "--engine-params",
                engine_params_string,
            ]
        )

    if engine is not None:
        workflow_run_cmd.extend(["--engine", engine])

    workflow_run = subprocess.run(
        workflow_run_cmd,
        capture_output=True,
        text=True,
    )

    if workflow_run.returncode == 0:
        try:
            workflow_run_json = json.loads(workflow_run.stdout)
            workflow_run_id = workflow_run_json["runs"][0]["run_id"]
            if workflow_run_id is None:
                logger.error(
                    f"\t✗ Something went wrong when submitting the workflow\n{workflow_run_json['runs'][0]['msg']}"
                )
                raise SystemExit(1)
        except json.JSONDecodeError as e:
            logger.error(f"\t✗ Error parsing JSON: {e}")
            raise SystemExit(1)
    else:
        logger.error(
            f"\t✗ Something went wrong when submitting the worklfow\n{workflow_run.stderr}"
        )
        raise SystemExit(1)

    logger.debug(f"\t➜ {family_id} submitted")
    return WORKFLOW_RUNNING_STATE


def main():
    args = parse_args()

    setup_logger(args.verbose)

    # Import backend-specific functions
    backend_module = import_backend_module(args.backend)

    # Bucket configuration
    if args.backend == "AZURE":
        storage_account = args.organization
        raw_data_bucket = f"{storage_account}/rawdata"
        reference_inputs_bucket = f"{storage_account}/referenceinputs"
        workflow_file_outputs_bucket = f"{storage_account}/workflowfile"
    else:
        organization = args.organization
        raw_data_bucket = f"{organization}-raw-data"
        reference_inputs_bucket = f"{organization}-reference-inputs"
        workflow_file_outputs_bucket = f"{organization}-workflow-file-outputs"

    # Make sure workflow is registered; defaults and transformations are set
    logger.info("Configuring workbench")
    subprocess.run(["omics", "use", WORKBENCH_URL])
    logger.debug("\t✓ Workbench configured")

    logger.info(
        f"Configuring workflow in Workbench ([{WORKFLOW_NAME}:{DERIVED_WORKFLOW_VERSION}])"
    )

    container_registry = (
        (f"{AWS_CONTAINER_REGISTRY_ACCOUNT}.dkr.ecr.{args.region}.amazonaws.com")
        if args.backend == "AWS"
        else None
    )
    static_inputs = backend_module.get_static_workflow_inputs(
        reference_inputs_bucket,
        workflow_file_outputs_bucket,
        args.region,
        container_registry,
    )
    workflow_id = configure_workflow(
        WORKFLOW_NAME,
        DERIVED_WORKFLOW_VERSION,
        args.backend,
        args.region,
        static_inputs,
        args.namespace,
    )
    logger.info("\t✓ Successfully configured workflow")
    logger.debug(f"\tWorkflow ID: {workflow_id}")
    logger.debug(f"\tWorkflow version: {DERIVED_WORKFLOW_VERSION}")

    if args.setup_only is False:
        sample_info = load_sample_info(args.sample_info, args.movie_bams, args.fam_info)

        logger.info("Formatting sample information")
        sample_info = validate_format_sample_info(sample_info)
        logger.debug("\t✓ Sample information formatted")

        logger.info(
            "Confirming that the raw data bucket exists, and that you have access to it"
        )
        raw_data_bucket, path_prefix = backend_module.validate_bucket(raw_data_bucket)

        # Upload the sample sync file to allow samples to be picked up in Instruments
        package_path = pkg_resources.resource_filename("hifi_solves_run_humanwgs", "")
        sample_sync_file_path = os.path.join(
            package_path, "instruments", "dnastack.sample-sync.json"
        )
        logger.info("Checking for presence of sample sync file")
        backend_module.upload_sample_sync_file(raw_data_bucket, sample_sync_file_path)

        sample_info, pending_families = upload_files(
            sample_info,
            backend_module,
            raw_data_bucket,
            args.backend,
            path_prefix,
        )

        if args.upload_only:
            if len(pending_families) == 0:
                logger.info("✓ All workflow files exist at destination")
            else:
                logger.info(
                    f"~ {len(pending_families)} families awaiting pending file transfer\n\t{pending_families}"
                )
        else:
            unique_family_ids = sample_info["family_id"].unique()
            if len(unique_family_ids) > 0:
                logger.info("Checking workflow run status and triggering new runs")
            else:
                logger.info("No workflow runs to trigger at present")

            run_states = {
                WORKFLOW_PENDING_UPLOAD_STATE: len(pending_families),
                WORKFLOW_UNSUBMITTED_STATE: len(unique_family_ids),
                WORKFLOW_RUNNING_STATE: 0,
                WORKFLOW_SUCCEEDED_STATE: 0,
                WORKFLOW_FAILED_STATE: 0,
            }

            failed_families = []

            for family_id in unique_family_ids:
                family_sample_data = sample_info[sample_info["family_id"] == family_id]

                workflow_inputs, engine_params = backend_module.generate_inputs_json(
                    family_sample_data,
                    reference_inputs_bucket,
                    workflow_file_outputs_bucket,
                    args.region,
                    container_registry,
                    aws_storage_capacity=args.aws_storage_capacity,
                )

                run_tags = get_tags(workflow_inputs)

                if args.write_inputs_json:
                    write_inputs_json(
                        family_id.replace(" ", "_"),
                        workflow_inputs,
                        engine_params,
                        run_tags,
                    )

                family_run_state = trigger_workflow_run(
                    family_id,
                    workflow_inputs,
                    workflow_id,
                    DERIVED_WORKFLOW_VERSION,
                    args.engine,
                    engine_params,
                    run_tags,
                    args.force_rerun,
                )
                run_states[family_run_state] += 1
                run_states[WORKFLOW_UNSUBMITTED_STATE] -= 1
                if family_run_state == WORKFLOW_FAILED_STATE:
                    failed_families.append(family_id)

            # Workflow run summary
            logger.info("Workflow run summary")
            for state, count in run_states.items():
                logger.info(f"\t{WORKFLOW_STATE_SYMBOLS[state]} {count} {state}")

            if len(failed_families) > 0:
                logger.info(f"Families with failed runs:\n{failed_families}")


if __name__ == "__main__":
    main()
