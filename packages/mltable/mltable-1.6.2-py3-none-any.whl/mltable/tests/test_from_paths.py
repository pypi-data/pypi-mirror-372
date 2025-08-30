import os

import pytest

from mltable.mltable import from_paths
from .helper_functions import mltable_was_loaded


@pytest.mark.mltable_sdk_unit_test
class TestFromPaths():
    def test_create_mltable_from_paths_with_local_abs_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(os.path.join(cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_paths(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (1, 1)
        assert list(df.columns) == ['Path']

    def test_create_mltable_from_paths_with_local_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'}]
        mltable = from_paths(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (1, 1)
        assert list(df.columns) == ['Path']

    def test_create_mltable_from_paths_with_local_paths(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'},
                 {'file': 'data/crime-winter.csv'}]
        mltable = from_paths(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (2, 1)
        assert list(df.columns) == ['Path']

    def test_create_mltable_from_paths_with_folder_local_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'folder': 'data/mltable/mltable_folder'}]
        mltable = from_paths(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (2, 1)
        assert list(df.columns) == ['Path']

    def test_create_mltable_from_paths_with_cloud_path(self):
        paths = [{'file': "https://dprepdata.blob.core.windows.net/demo/Titanic2.csv"}]
        mltable = from_paths(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (1, 1)
        assert list(df.columns) == ['Path']
