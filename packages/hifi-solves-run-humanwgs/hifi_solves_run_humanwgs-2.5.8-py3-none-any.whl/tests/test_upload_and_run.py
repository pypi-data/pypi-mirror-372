#!/usr/bin/env python3

import unittest
from hifi_solves_run_humanwgs.upload_and_run import (
    load_sample_info,
    validate_format_sample_info,
)
from hifi_solves_run_humanwgs.logger import logger

import pandas as pd


class TestValidateFormatSampleInfo(unittest.TestCase):
    expected_sample_info = pd.DataFrame.from_records(
        [
            (
                "HG005-fam",
                "HG005",
                ["movie1.bam", "movie2.bam"],
                "HG006",
                "HG007",
                "MALE",
                False,
            ),
            ("HG005-fam", "HG006", ["movie3.bam"], None, None, "MALE", False),
            ("HG005-fam", "HG007", ["movie4.bam"], None, None, "FEMALE", False),
        ],
        columns=[
            "family_id",
            "sample_id",
            "hifi_reads",
            "father_id",
            "mother_id",
            "sex",
            "affected",
        ],
    ).set_index("sample_id", drop=False)

    expected_sample_info_multiple_families = pd.DataFrame.from_records(
        [
            ("HG002-fam", "HG002", ["movie5.bam"], "HG003", "HG004", "MALE", False),
            ("HG002-fam", "HG003", ["movie6.bam"], None, None, "MALE", False),
            ("HG002-fam", "HG004", ["movie7.bam"], None, None, "FEMALE", False),
            (
                "HG005-fam",
                "HG005",
                ["movie1.bam", "movie2.bam"],
                "HG006",
                "HG007",
                "MALE",
                False,
            ),
            ("HG005-fam", "HG006", ["movie3.bam"], None, None, "MALE", False),
            ("HG005-fam", "HG007", ["movie4.bam"], None, None, "FEMALE", False),
        ],
        columns=[
            "family_id",
            "sample_id",
            "hifi_reads",
            "father_id",
            "mother_id",
            "sex",
            "affected",
        ],
    ).set_index("sample_id", drop=False)

    def test_missing_required_family_id_column(self):
        sample_info = pd.DataFrame(
            {
                "sample_id": ["HG002", "HG003", "HG004"],
                "movie_bams": ["_HG002.bam", "_HG003.bam", "_HG004.bam"],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Missing required columns: family_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_missing_required_sample_id_column(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "movie_bams": ["_HG002.bam", "_HG003.bam", "_HG004.bam"],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Missing required columns: sample_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_missing_required_movie_bams_column(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG003", "HG004"],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Missing required columns: movie_bams",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_missing_multiple_required_columns(self):
        sample_info = pd.DataFrame(
            {
                "sample_id": ["HG002", "HG003", "HG004"],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Missing required columns: family_id, movie_bams",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_invalid_sex(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG002", "HG004"],
                "movie_bams": ["_HG002.bam", "_HG002_2.bam", "_HG004.bam"],
                "sex": ["Male", None, "fem"],
            }
        )
        with self.assertRaisesRegex(KeyError, "Invalid sex"):
            validate_format_sample_info(sample_info)

    def test_one_unique_value_of_mother_id(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG002", "HG004"],
                "movie_bams": ["_HG002.bam", "_HG002_2.bam", "_HG004.bam"],
                "mother_id": ["HG001", "HG003", None],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "There should be exactly one unique value of mother_id for each combination of family_id, sample_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_one_unique_value_of_father_id(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG002", "HG004"],
                "movie_bams": ["_HG002.bam", "_HG002_2.bam", "_HG004.bam"],
                "father_id": ["HG001", "HG003", None],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "There should be exactly one unique value of father_id for each combination of family_id, sample_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_one_unique_value_of_sex(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG002", "HG004"],
                "movie_bams": ["_HG002.bam", "_HG002_2.bam", "_HG004.bam"],
                "sex": ["Male", "Female", None],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "There should be exactly one unique value of sex for each combination of family_id, sample_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_no_missing_values_in_required_columns(self):
        sample_info = pd.DataFrame(
            {
                "family_id": ["HG002_cohort", "HG002_cohort", "HG002_cohort"],
                "sample_id": ["HG002", "HG003", "HG004"],
                "movie_bams": ["_HG002.bam", None, "_HG004.bam"],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Missing values found in required columns: movie_bams",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_no_duplicate_movie_bams_in_different_samples(self):
        sample_info = pd.DataFrame(
            {
                "family_id": [
                    "HG002_cohort",
                    "HG002_cohort",
                    "HG002_cohort",
                    "HG002_cohort",
                ],
                "sample_id": ["HG002", "HG003", "HG004", "HG004"],
                "movie_bams": [
                    "_HG002.bam",
                    "_HG003.bam",
                    "_HG003.bam",
                    "_HG004.bam",
                ],
            }
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "\t✗ Duplicate movie bams found: _HG003.bam",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_load_with_no_phenotypes(self):
        sample_info = load_sample_info("tests/data/hg005.sample_info.csv", None, None)
        formatted_sample_info = validate_format_sample_info(sample_info)
        self.assertTrue(formatted_sample_info.equals(self.expected_sample_info))

    def test_load_with_phenotypes(self):
        sample_info = load_sample_info(
            "tests/data/hg005.sample_info.with_phenotypes.csv", None, None
        )
        formatted_sample_info = validate_format_sample_info(sample_info)
        self.assertTrue(formatted_sample_info.equals(self.expected_sample_info))

    def test_load_with_no_phenotypes_from_fam(self):
        sample_info = load_sample_info(
            None,
            "tests/data/hg005.movie_bams.csv",
            "tests/data/hg005.no_phenotypes.fam",
        )
        formatted_sample_info = validate_format_sample_info(sample_info)
        self.assertTrue(formatted_sample_info.equals(self.expected_sample_info))

    def test_load_with_phenotypes_from_fam(self):
        sample_info = load_sample_info(
            None, "tests/data/hg005.movie_bams.csv", "tests/data/hg005.fam"
        )
        formatted_sample_info = validate_format_sample_info(sample_info)
        self.assertTrue(formatted_sample_info.equals(self.expected_sample_info))

    # tests for multiple families
    def test_load_multiple_fams_ok(self):
        sample_info = load_sample_info("tests/data/multiple_families.csv", None, None)
        formatted_sample_info = validate_format_sample_info(sample_info)
        self.assertTrue(
            formatted_sample_info.equals(self.expected_sample_info_multiple_families)
        )

    def test_sample_unique_across_families(self):
        sample_info = load_sample_info(
            "tests/data/multiple_families.duplicated_sample.csv", None, None
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "The same sample was found under multiple family IDs; please ensure sample_ids are unique.",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)

    def test_parent_not_found_in_family(self):
        sample_info = load_sample_info(
            "tests/data/multiple_families.bad_parents.csv", None, None
        )
        with self.assertLogs(logger, level="ERROR") as log_capture, self.assertRaises(
            SystemExit
        ) as exit_capture:
            validate_format_sample_info(sample_info)

        self.assertIn(
            "Mother or father ID for samples given were either not found in the cohort, or have a different family_id",
            log_capture.output[0],
        )
        self.assertEqual(exit_capture.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
