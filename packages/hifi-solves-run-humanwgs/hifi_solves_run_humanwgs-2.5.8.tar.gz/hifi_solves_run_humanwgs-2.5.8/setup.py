from setuptools import setup, find_packages

version = "2.5.8"

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="hifi_solves_run_humanwgs",
    version=version,
    description="Upload required files and run [PacBio's Human WGS workflow](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL) via [DNAstack's Workbench](https://omics.ai/workbench/)",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="DNAstack",
    author_email="bioinformatics@dnastack.com",
    maintainer="Heather Ward",
    maintainer_email="heather@dnastack.com",
    license="GPLv2",
    license_files="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    package_data={"upload_and_run.workflows": ["*.wdl"]},
    entry_points={
        "console_scripts": [
            "run-humanwgs = hifi_solves_run_humanwgs.upload_and_run:main",
            "hifisolves-ingest = hifi_solves_run_humanwgs.upload_and_run:main",
        ],
    },
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.2.2",
        "boto3>=1.34.0",
        "dnastack-client-library==v3.1.114a",
        "azure-storage-blob==12.20.0",
        "azure-core==1.30.2",
        "google-cloud-storage==2.17.0",
        "regex==2024.11.6",
    ],
)
