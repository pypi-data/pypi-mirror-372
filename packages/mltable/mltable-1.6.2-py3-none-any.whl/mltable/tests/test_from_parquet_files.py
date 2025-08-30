import os

import pytest

from mltable.mltable import from_parquet_files
from .helper_functions import mltable_was_loaded


@pytest.mark.mltable_sdk_unit_test
class TestFromParquetFiles():
    def test_create_mltable_with_local_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime.parquet'}]
        mltable = from_parquet_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (10, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_with_local_folder_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'folder': 'data/mltable/mltable_folder_parquet'}]
        mltable = from_parquet_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_with_local_paths(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/mltable/mltable_folder_parquet/crime.parquet'},
                 {'file': 'data/mltable/mltable_folder_parquet/crime_2.parquet'}]
        mltable = from_parquet_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_with_local_abs_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(os.path.join(cwd, 'data/crime.parquet'))
        paths = [{'file': exp_path_1}]
        mltable = from_parquet_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (10, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_include_path_column(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime.parquet'}]
        mltable = from_parquet_files(paths, include_path_column=True)
        df = mltable_was_loaded(mltable)
        assert df.shape == (10, 23)
        assert list(df.columns) == [
            'Path', 'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description',
            'Location Description', 'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code',
            'X Coordinate', 'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]
