# HiFi Solves Human WGS workflow runner

As part of [the HiFi Solves Consortium](https://hifisolves.org/collections), organizations will run their sequencing data through [PacBio's Human Whole Genome Sequencing (WGS) pipeline](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL).

This package handles uploading all required raw data to the organization's cloud, configures the required workflow metadata, and triggering a run of the HumanWGS workflow. Output files are automatically ingested into Publisher and made available on [hifisolves.org](https://hifisolves.org/collections).

## Package information

- HumanWGS pipeline version: [`v2.1.1`](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/releases/tag/v2.1.1)

### Requirements

- python3.9+
- An engine registered on Workbench
- Credentials for the relevant backend (supported backends: AWS, Azure, GCP)

## Installation

`python3 -m pip install hifi-solves-run-humanwgs`

# Script usage

## Arguments

```bash
usage: hifisolves-ingest [-h] [-v] [-s SAMPLE_INFO] [-m MOVIE_BAMS] [-c FAM_INFO] -b {AWS,GCP,AZURE} -r REGION -o ORGANIZATION [-e ENGINE] [-u] [-i] [-f]
                         [--aws-storage-capacity AWS_STORAGE_CAPACITY]

Upload genomics data and run PacBio's official Human WGS pipeline

options:
  -h, --help            show this help message and exit
  -v, --version         Program version
  -b {AWS,GCP,AZURE}, --backend {AWS,GCP,AZURE}
                        Backend where infrastructure is set up
  -r REGION, --region REGION
                        Region where infrastructure is set up
  -o ORGANIZATION, --organization ORGANIZATION
                        Organization identifier; used to infer bucket names
  -e ENGINE, --engine ENGINE
                        Engine to use to run the workflow. Defaults to the default engine set in Workbench.
  -u, --upload-only     Upload movie BAMs and generate inputs JSON only; do not submit the workflow. If set, --write-inputs-json will also be set automatically.
  -i, --write-inputs-json
                        Write inputs JSON and engine configuration to a file. Files will be named {family_id}.inputs.json, {family_id}.engine_params.json, {family_id}.run_tags.json.
  -f, --force-rerun-failed
                        Force rerun samples that have previously been run and failed; will not rerun samples that are currently running or have a succeeded run.
  --aws-storage-capacity AWS_STORAGE_CAPACITY
                        Storage capacity override for AWS HealthOmics backend. Defaults to total size of input BAMs across all samples * 8. Supply either the requested storage capacity in GB, or 'DYNAMIC' to set storage to dynamic.

Sample information:
  Provide either --sample-info, OR both --movie-bams and --fam-info

  -s SAMPLE_INFO, --sample-info SAMPLE_INFO
                        Path to sample info CSV or TSV. This file should have columns [family_id, sample_id, movie_bams, father_id, mother_id, sex]. See documentation for more information on the format of this file.
  -m MOVIE_BAMS, --movie-bams MOVIE_BAMS
                        Path to movie bams CSV or TSV. This file should have columns [sample_id, movie_bams]. Repeated rows for each sample can be added if the sample has more than one associated movie bam.
  -c FAM_INFO, --fam-info FAM_INFO
                        Path to family information. This file should have columns [family_id, sample_id, father_id, mother_id, sex]. It can optionally have additional phenotype columns (columns 6-end), but this information will not be used.

```

## Sample info file

The sample info file defines the set of samples that will be run through the workflow. The workflow can either be run on individual samples or on families (typically trios, where sequencing data exists for the mother, father, and child). One workflow run will be submitted for each unique family ID, including all samples that share that family ID.

This information is organized into a CSV file with the following columns:

| Column name              | Description                                                                                                                                            |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `family_id`              | Unique identifier for this family / cohort. If you are running a single sample through the workflow, this can be set to the same value as `sample_id`. |
| `sample_id`              | Sample identifier                                                                                                                                      |
| `movie_bams`<sup>†</sup> | Local path to a BAM file (either movie BAM or aligned BAM) associated with this sample                                                                 |
| `father_id`              | sample_id of the father. This field can be left blank if the sample's father is not included in the run.                                               |
| `mother_id`              | sample_id of the mother. This field can be left blank if the sample's mother is not included in the run.                                               |
| `sex`                    | Set to either "MALE" or "FEMALE"                                                                                                                       |

† There can be more than one BAM for a sample. If this is the case, a new row should be generated for each additional movie_bam; `family_id` and `sample_id` must be set for these fields, but information from other fields need not be repeated.

### Example sample info files

All samples for all runs (singleton and family-based runs) may be included in a single sample info file; a separate run will be submitted for every unique family ID in the `sample_info` CSV.

#### Singleton

Here we have a single sample, HG005, with two associated movie bams found at the local paths `bams/HG005_1.hifi_reads.bam` and `bams/HG005_2.hifi_reads.bam`. The sample is being run alone so `father_id` and `mother_id` are left blank. Sex information only needs to be included once and can be omitted for further rows associated with the same `sample_id`.

```csv
family_id,sample_id,movie_bams,father_id,mother_id,sex
HG005,HG005,bams/HG005_1.hifi_reads.bam,,,MALE
HG005,HG005,bams/HG005_2.hifi_reads.bam,,,
```

#### Trio

Here we have a trio of samples: a child (HG005), father (HG006), and mother (HG007). The mother and father samples have several associated `movie_bams`, so there are multiple rows for each.

```csv
family_id,sample_id,movie_bams,father_id,mother_id,sex
hg005-trio,HG005,bams/HG005_1.hifi_reads.bam,HG006,HG007,MALE
hg005-trio,HG006,bams/HG006_1.hifi_reads.bam,,,MALE
hg005-trio,HG006,bams/HG006_2.hifi_reads.bam,,,
hg005-trio,HG007,bams/HG007_1.hifi_reads.bam,,,FEMALE
hg005-trio,HG007,bams/HG007_2.hifi_reads.bam,,,
hg005-trio,HG007,bams/HG007_3.hifi_reads.bam,,,
```

## Alternative to the sample info file - --movie-bams and --fam-info

Instead of providing a `--sample-info` file, you may choose to organize your information into two separate files: `--movie-bams`, and `--fam-info`.

### Movie bams

Provided using the `--movie-bams` argument.

| Column name              | Description                                                |
| :----------------------- | :--------------------------------------------------------- |
| `sample_id`              | Sample identifier                                          |
| `movie_bams`<sup>†</sup> | Local path to a movie BAM file associated with this sample |

† There can be more than one movie bam for a sample. If this is the case, a new row should be generated for each additional movie_bam.

#### Example movie bam file

```csv
sample_id,movie_bams
HG005,bams/HG005_1.hifi_reads.bam
HG006,bams/HG006_1.hifi_reads.bam
HG006,bams/HG006_2.hifi_reads.bam
HG007,bams/HG007_1.hifi_reads.bam
HG007,bams/HG007_2.hifi_reads.bam
HG007,bams/HG007_3.hifi_reads.bam
```

### Family information

Provided using the `--fam-info` argument. This file is related to [PLINK's fam info format](https://www.cog-genomics.org/plink/1.9/formats#fam), with some modifications (namely, a header is required, and there can be multiple (or zero) phenotypes columns; note that phenotype information is discarded here).

| Column name | Description                                                                                                                                            |
| :---------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `family_id` | Unique identifier for this family / cohort. If you are running a single sample through the workflow, this can be set to the same value as `sample_id`. |
| `sample_id` | Sample identifier                                                                                                                                      |
| `father_id` | sample_id of the father. This field can be left blank if the sample's father is not included in the run.                                               |
| `mother_id` | sample_id of the mother. This field can be left blank if the sample's mother is not included in the run.                                               |
| `sex`       | 1=male, 2=female                                                                                                                                       |

#### Example fam info file

```csv
family_id,sample_id,father_id,mother_id,sex,HP:0001250,HP:0001263
hg005-trio,HG005,HG006,HG007,1,2,2
hg005-trio,HG006,,,1,1,1
hg005-trio,HG007,,,2,1,1
```

# Running the script

By default, the script will both upload input files and trigger workflow runs.

To upload input files only, run using the `--upload-only` flag.

## Example run command - AWS

The AWS HealthOmics backend requires storage capacity for the run to be set; this capacity includes all inputs, outputs, and intermediate workflow files that are generated during workflow execution. The script will attempt to estimate the required capacity based on the size of input files, but this value can be overridden by setting the `--aws-storage-capacity` flag to either:

- 'DYNAMIC': storage will scale dynamically as the workflow runs; you should theoretically not run out of storage space
- `<storage_capacity_gb>`: the storage capacity in GB, between 0 and 9600 (9.6 TB)

See [the HealthOmics docs](https://docs.aws.amazon.com/omics/latest/dev/workflows-run-types.html) for more information on run storage.

```bash
# AWS credentials
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""

AWS_REGION=""
# Used for naming upload and output buckets
ORGANIZATION=""

hifisolves-ingest \
    --sample-info sample_info.csv \
    --backend aws \
    --region "${AWS_REGION}" \
    --organization "${ORGANIZATION}"
```

## Example run command - Azure

```bash
# Azure credentials; needs Read, Add, Write, Create, Delete, List
export AZURE_STORAGE_SAS_TOKEN=""

AZURE_REGION=""
# Used for naming upload and output buckets; this is going to be == the storage account name
ORGANIZATION=""

hifisolves-ingest \
    --sample-info sample_info.csv \
    --backend Azure \
    --region "${AZURE_REGION}" \
    --organization "${ORGANIZATION}"
```

If you have files already uploaded in the target storage account, their paths may be referenced in the format `/<storage_account>/rawdata/path/to/file`.

### Copying Azure <> Azure

If source files are currently in cloud storage, they can be copied into the target storage account rather than copying from local -> cloud.

BAM URLs in the `sample_info` CSV file should be in the format `/<src_storage_account>/<src_storage_container>/path/to/movie.bam`.

An additional env variable, `SOURCE_CONTAINER_SAS_TOKEN`, should be defined. This SAS token should have Read and List permissions on the source container.

```bash
# SAS token for the source bucket (R/L)
export SOURCE_CONTAINER_SAS_TOKEN=""

# SAS token for the destination bucket (R/A/W/C/D/L)
export AZURE_STORAGE_SAS_TOKEN=""

AZURE_REGION=""
ORGANIZATION=""

hifisolves-ingest \
    --sample-info sample_info.csv \
    --backend Azure \
    --region "${AZURE_REGION}" \
    --organization "${ORGANIZATION}"
```

## Example run command - GCP

```bash
# GCP credentials - GOOGLE_APPLICATION_CREDENTIALS should point towards a JSON file containing service account information
export GOOGLE_APPLICATION_CREDENTIALS=""

GCP_REGION=""
# Used for naming upload and output buckets
ORGANIZATION=""

hifisolves-ingest \
	--sample-info sample_info.csv \
	--backend gcp \
	--region "${GCP_REGION}" \
	--organization "${ORGANIZATION}"
```

# Development

## Tests

_Note that you will need access to have the active cloud-specific credentials below set for the various cloud backends to run the tests._

See [this secret](https://start.1password.com/open/i?a=7NPE3CP55BHD5FCTKGQYWMT2XU&v=tyykwlqgisiv33exjxnnln3434&i=lltbwiedpo7igirwlhmo27jz3e&h=team-dnastack.1password.com) for the values you'll need to set here.

```bash
# Required AWS credentials
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""
# alternatively - just AWS_PROFILE
# export AWS_PROFILE=""

# Required Azure credentials
_Note that these credentials will eventually expire_
# R/A/W/C/D/L on destination container
export AZURE_STORAGE_SAS_TOKEN=""
# R/L on src container
export SOURCE_CONTAINER_SAS_TOKEN=""

# Path to service account JSON
export GOOGLE_APPLICATION_CREDENTIALS=""
```

`python3 -m unittest discover -b -s tests`

## Setting the workflow version

The workflow version is comprised of [two parts](https://github.com/DNAstack/hifi-solves-run-humanwgs/blob/main/hifi_solves_run_humanwgs/constants.py#L3-L4):

- `WORKFLOW_VERSION`: This is the version of the HumanWGS workflow in use; it should refer to a specific tagged version of this workflow
- `WORKFLOW_SUB_VERSION`: This is the revision of the HumanWGS workflow, and is used when we need to make changes to the workflow that are not present in PacBio's official workflow

Changing any part of either of these versions will force a new version of the workflow to be created in the user's namespace. Changing the `WORKFLOW_VERSION` or the major version of the `WORKFLOW_SUB_VERSION` will also result in the script resetting the run status for all samples back to unprocessed; changing just the minor or patch version of `WORKFLOW_SUB_VERSION` will allow any run with the same major `WORKFLOW_SUB_VERSION` to be picked up & used to determine run status. This allows small bugfixes to be made to the workflow in order to enable running samples without the need to fully reprocess all samples when a new version of the workflow is registered.

## Setting workflow version automatically using a Git hook

There are two locations where the workflow version is set manually ([in constants.py](./hifi_solves_run_humanwgs/constants.py#L3) and [in the hifisolves_wrapper workflow itself](./hifi_solves_run_humanwgs/workflows/hifisolves_wrapper.wdl#L35)). This may lead to issues when there is a new release and fork of the HumanWGS pipeline and these values are not adjusted accordingly. Running the below will set the path to the Git hooks directory to our custom `hooks` directory and run a blank `git checkout` command, which invokes the `post-checkout` hook and sets the workflow version in both of the aforementioned locations.

**Note**: The command will need to be run from the root of the repository (`hifi-solves-run-humanwgs`)

```
git config core.hooksPath hooks/ && git checkout
```
