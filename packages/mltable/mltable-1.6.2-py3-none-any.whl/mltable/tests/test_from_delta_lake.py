import os

import pandas as pd
import pytest
from azureml.dataprep import UserErrorException

from mltable.mltable import from_delta_lake, load
from .helper_functions import can_load_mltable


@pytest.mark.mltable_sdk_unit_test
@pytest.mark.skip(reason=("mltable-sdk-unit only picks up azureml-dataprep from public pypi that is currently broken. "
                          "Disabling to merge the fix and unblock PRs"))
class TestFromDeltaLake:
    def test_from_local_delta_table_version(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        delta_table_path = "data/mltable/delta-table"

        mltable_v0 = from_delta_lake(delta_table_path, version_as_of=0)
        df_v0 = mltable_v0.to_pandas_dataframe()
        assert df_v0.shape == (5, 1)
        assert df_v0["id"].equals(pd.Series([0, 1, 2, 3, 4]))

        mltable_v1 = from_delta_lake(delta_table_path, version_as_of=1, include_path_column=True)
        df_v1 = mltable_v1.to_pandas_dataframe()
        assert df_v1.shape == (5, 2)
        assert df_v1["id"].equals(pd.Series([5, 6, 7, 8, 9]))

    def test_from_local_delta_table_timestamp(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        delta_table_path = "data/mltable/delta-table"

        mltable_t0 = from_delta_lake(delta_table_path, timestamp_as_of="2021-01-01T00:00:00Z")
        df_t0 = mltable_t0.to_pandas_dataframe()
        assert df_t0.shape == (5, 1)
        assert df_t0["id"].equals(pd.Series([0, 1, 2, 3, 4]))

        mltable_t1 = from_delta_lake(delta_table_path,
                                     timestamp_as_of="2021-08-09T01:30:00Z",
                                     include_path_column=True)
        df_t1 = mltable_t1.to_pandas_dataframe()
        assert df_t1.shape == (5, 2)
        assert df_t1["id"].equals(pd.Series([5, 6, 7, 8, 9]))

    def test_load_local_mltable_from_delta_lake_version_1(self, get_dir_folder_path):
        wd = get_dir_folder_path
        mltable_path = os.path.join(wd, "data/mltable/delta-table/")
        df_v1 = can_load_mltable(mltable_path)
        assert df_v1.shape == (5, 1)
        assert df_v1["id"].equals(pd.Series([5, 6, 7, 8, 9]))

    def test_from_delta_lake_with_both_timestamp_and_version(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        delta_table_path = "data/mltable/delta-table"
        exp_err_msg = ("Both timestamp_as_of and version_as_of parameters were provided, "
                       "but only one of version_as_of or timestamp_as_of can be specified.")
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delta_lake(delta_table_path, version_as_of=1, timestamp_as_of="2021-08-09T01:30:00Z")

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_missing_0_in_month(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-8-09T01:30:00Z')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_missing_0_in_date(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-9T01:30:00Z')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_missing_0_in_hour(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-09T1:30:00Z')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_missing_seconds(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-09T01:30Z')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_missing_time(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-09')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_zero_timezone_and_time_offset_specified(
            self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-09T01:30:00Z-07:00')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_seconds_on_time_offset_specified(
            self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(
            get_dir_folder_path, '2021-08-09T01:30:00-07:00:00')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_space_separates_date_and_time(
            self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '2021-08-09 01:30:00-07:00')

    def test_from_delta_lake_with_non_rfc3339_format_timestamp_no_hypens_and_colons(self, get_dir_folder_path):
        self.run_from_delta_lake_with_non_rfc3339_format_timestamps(get_dir_folder_path, '20210809T013000Z')

    def run_from_delta_lake_with_non_rfc3339_format_timestamps(self, cwd, timestamp):
        os.chdir(cwd)
        exp_err_msg = (f'Provided timestamp_as_of: {timestamp} is not in RFC-3339/ISO-8601 format\\. Please make sure '
                       'that it adheres to RFC-3339/ISO-8601 format\\. For example: "2022-10-01T00:00:00Z", '
                       '"2022-10-01T22:10:57\\+02:00", "2022-10-01T16:32:11\\.8\\+00:00" are correctly formatted\\.')
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delta_lake("data/mltable/delta-table", timestamp_as_of=timestamp)

    def test_from_delta_lake_with_valid_rfc3339_format_timestamps(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        delta_table_path = "data/mltable/delta-table"
        t0 = "2021-01-01T00:00:00+08:00"  # using + time offset
        mltable_t0 = from_delta_lake(delta_table_path, timestamp_as_of=t0)
        df_t0 = mltable_t0.to_pandas_dataframe()
        assert df_t0.shape == (5, 1)
        assert df_t0["id"].equals(pd.Series([0, 1, 2, 3, 4]))

        t1 = "2021-08-09T01:30:00-08:00"  # using - time offset
        mltable_t1 = from_delta_lake(delta_table_path, timestamp_as_of=t1, include_path_column=True)
        df_t1 = mltable_t1.to_pandas_dataframe()
        assert df_t1.shape == (5, 2)
        assert df_t1["id"].equals(pd.Series([5, 6, 7, 8, 9]))

        # using fractional second digits + time offset
        t2 = "2021-01-01T00:00:00.238016+08:00"
        mltable_t2 = from_delta_lake(delta_table_path, timestamp_as_of=t2)
        df_t2 = mltable_t2.to_pandas_dataframe()
        assert df_t2.shape == (5, 1)
        assert df_t2["id"].equals(pd.Series([0, 1, 2, 3, 4]))

        # using fractional second digits + zero time offset
        t3 = "2021-08-09T01:30:00.238016Z"
        mltable_t3 = from_delta_lake(delta_table_path, timestamp_as_of=t3, include_path_column=True)
        df_t3 = mltable_t3.to_pandas_dataframe()
        assert df_t3.shape == (5, 2)
        assert df_t3["id"].equals(pd.Series([5, 6, 7, 8, 9]))


@pytest.mark.mltable_sdk_unit_test
class TestFromDeltaLakeUserErrors:
    def test_from_local_both_version_and_timestamp(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        mltable_path = os.path.join(cwd, "data/mltable/delta-table-both-version-and-timestamp/")
        with pytest.raises(UserErrorException,
                           match="Only one of version or timestamp can be specified but not both..*"):
            mltable = load(mltable_path)
            mltable.to_pandas_dataframe()

    def test_from_local_unable_to_find_metadata(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        # test using a non delta table MLTable directory
        delta_table_path = "data/mltable/mltable_folder"
        with pytest.raises(UserErrorException, match="Unable to find any delta table metadata.*"):
            mltable = from_delta_lake(delta_table_path, version_as_of=0)
            mltable.to_pandas_dataframe()

    def test_from_local_invalid_table_version(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        delta_table_path = "data/mltable/delta-table"
        with pytest.raises(UserErrorException) as e:
            mltable = from_delta_lake(delta_table_path, version_as_of=100000)
            mltable.to_pandas_dataframe()
            assert "Error when opening delta table: Invalid table version: 100000" in e.message
