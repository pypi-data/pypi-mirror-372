import copy
import os

from azureml.dataprep import UserErrorException
import pytest
import yaml

from mltable.mltable import MLTable, _check_no_dup_cols, load
from mltable._utils import _validate, _path_is_current_directory_variant, _make_all_paths_absolute


@pytest.mark.mltable_sdk_unit_test
class TestMLTableInnerFunctions:
    """
    This class is for adding unit tests related to internal/helper functions that are called by MLTable APIs
    """
    def test_update_workspace_info(self):
        mlt_strs = ["""
        paths:
          - file: ./train_annotations.jsonl
        transformations:
          - read_json_lines:
                encoding: utf-8
                include_path_column: false
          - convert_column_types:
              - columns: image_url
                column_type: stream_info
        """, """
        paths:
          - file: ./train_annotations.jsonl
        transformations:
          - read_json_lines:
                encoding: utf8
                include_path_column: false
          - convert_column_types:
              - columns: image_url
                column_type: stream_info
          - convert_column_types:
              - columns: not_image_url
                column_type: stream_info
        """]

        expected_mlt_strs = ["""
        type: mltable
        paths:
          - file: "./train_annotations.jsonl"
        transformations:
          - read_json_lines:
              path_column: Path
              invalid_lines: error
              encoding: utf8
              include_path_column: false
              partition_size: 20971520
          - convert_column_types:
              - columns: image_url
                column_type:
                  stream_info:
                    subscription: test_sub
                    resource_group: test_rg
                    workspace_name: test_ws
                    escaped: false
        """, """
        type: mltable
        paths:
          - file: "./train_annotations.jsonl"
        transformations:
          - read_json_lines:
              path_column: Path
              invalid_lines: error
              encoding: utf8
              include_path_column: false
              partition_size: 20971520
          - convert_column_types:
              - columns: image_url
                column_type:
                  stream_info:
                    subscription: test_sub
                    resource_group: test_rg
                    workspace_name: test_ws
                    escaped: false
          - convert_column_types:
              - columns: not_image_url
                column_type: stream_info
        """]

        ws_info = {
            'subscription': 'test_sub',
            'resource_group': 'test_rg',
            'workspace': 'test_ws'
        }

        stream_column = 'image_url'
        for mlt_str, exp_mlt_str in zip(mlt_strs, expected_mlt_strs):
            mlt_dict = yaml.safe_load(mlt_str)
            mlt = MLTable._create_from_dict(mlt_dict, None, '')
            new_mlt = MLTable._append_workspace_to_stream_info_conversion(mlt, ws_info, stream_column)
            new_mlt_str = str(new_mlt)
            assert yaml.safe_load(new_mlt_str) == yaml.safe_load(exp_mlt_str)

    def run_no_dup_cols(self, cols):
        exp_err_msg = "Found duplicate column. Cannot convert column 'colA' to multiple `mltable.DataType`s."
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _check_no_dup_cols(cols)

    def test_no_dup_cols_tuple(self):
        self.run_no_dup_cols(('colA', 'colA'))

    def test_no_dup_columns_list(self):
        self.run_no_dup_cols(['colA', 'colA'])

    def test_no_dup_cols_list_of_tuples(self):
        self.run_no_dup_cols([('colA', 'colB'), ('colC', 'colA')])

    def test_get_columns_in_traits(self, get_data_folder_path):
        path = os.path.join(get_data_folder_path, 'traits_timeseries')
        mltable = load(path)
        assert mltable._get_columns_in_traits() == {'datetime'}

    def test_validate(self):
        error_key_mltable_yaml_dict = {
            'type': 'mltable',
            'path': [{'file': 'https://dprepdata.blob.core.windows.net/demo/Titanic2.csv'}],
            'transformations': [{'take': 1}]
        }

        error_value_mltable_yaml_dict = {
            'type': 'mltable',
            'paths': [{'file': './Titanic2.csv'}],
            'transformations': [{
                'read_delimited': {
                    'delimiter': ',', 'encoding': 'ascii', 'empty_as_string': False,
                    'header': 'dummy_value', 'infer_column_types': False
                }
            }]
        }

        exp_err_msg = "Additional properties are not allowed \\('path' was unexpected\\)"
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _validate(error_key_mltable_yaml_dict)

        exp_err_msg = "'dummy_value' is not one of " \
                      "\\['no_header', 'from_first_file', 'all_files_different_headers', 'all_files_same_headers'\\]"
        with pytest.raises(UserErrorException, match=exp_err_msg):
            _validate(error_value_mltable_yaml_dict)

    def test_path_is_current_directory_variant(self):
        base_dir_linux, base_dir_windows, base_dir_dot = './', '.\\', '.'
        non_base_dir = './Titanic2.csv'
        assert _path_is_current_directory_variant(base_dir_linux)
        assert _path_is_current_directory_variant(base_dir_windows)
        assert _path_is_current_directory_variant(base_dir_dot)
        assert not _path_is_current_directory_variant(non_base_dir)


@pytest.mark.mltable_sdk_unit_test
class TestMLTableMakeAllPathsAbsolute:
    def run_no_change(self, path, base_path):
        mltable_yaml_dict = {'paths': [{'file': path}]}
        result, _ = _make_all_paths_absolute(copy.deepcopy(mltable_yaml_dict), base_path)
        assert result is not mltable_yaml_dict
        assert result == mltable_yaml_dict

    def test_path_starts_with_file_header(self):
        self.run_no_change('file:///home/user/files/file.csv', '/swp/thing')

    def test_non_local_path(self):
        self.run_no_change('https://www.github.com/repo/test_csv', '/swp/thing')

    def test_cloud_path(self):
        self.run_no_change('https://dprepdata.blob.core.windows.net/demo/Titanic2.csv', '/mltable/dirc/path')

    def run_append_base_path(self, *paths, base_path='.'):
        base_path = os.path.abspath(base_path)
        mltable_yaml_dict = {'paths': [{'file': path} for path in paths]}
        result, _ = _make_all_paths_absolute(mltable_yaml_dict, base_path)
        exp_result = {'paths':
                      [{'file': 'file://' + os.path.join(base_path, os.path.normpath(path))}for path in paths]}

        assert len(result['paths']) == len(exp_result['paths'])
        for path_dict in result['paths']:
            assert path_dict in exp_result['paths']

    def test_local_happy_relative_paths(self, get_data_folder_path):
        base_path = os.path.join(get_data_folder_path, 'mltable_relative')
        self.run_append_base_path('Titanic2.csv', './subfolder/Titanic2.csv', base_path=base_path)

    def test_non_absolute_local_paths_made_absolute(self, get_data_folder_path):
        base_path = os.path.join(get_data_folder_path, 'mltable_relative')
        self.run_append_base_path('Titanic2.csv', './subfolder/Titanic2.csv', base_path=base_path)

    def test_non_absolute_basepath(self):
        self.run_append_base_path(
            'Titanic2.csv', './subfolder/Titanic2.csv', base_path='mltable_relative')

    def test_cwd_basepath(self):
        self.run_append_base_path(
            'Titanic2.csv', './subfolder/Titanic2.csv', base_path='.')

    def test_data_asset_uri_basepath(self):
        base_path = 'azureml://subscriptions/test/resourcegroups/rg/' \
                    'providers/Microsoft.MachineLearningServices/workspaces/ws/data/d/versions/1'
        self.run_append_base_path('Titanic2.csv', './subfolder/Titanic2.csv', base_path=base_path)

    def test_cloud_basepath(self):
        base_path = 'https://www.github.com/my/mltable/repo'
        self.run_append_base_path('Titanic2.csv', './subfolder/Titanic2.csv', base_path=base_path)

    def test_legacy_dataset_basepath(self):
        base_path = 'azureml://locations/azure_loc/workspaces/ws/data/d/versions/1'
        self.run_append_base_path('Titanic2.csv', './subfolder/Titanic2.csv', base_path=base_path)


@pytest.mark.mltable_sdk_unit_test_windows
class TestInnerFunctionsWindowsOnly:
    def test_make_all_paths_absolute_local_relative_path_double_backslash(self, get_data_folder_path):
        base_path = os.path.join(get_data_folder_path, os.path.join('dummy_basepath', 'inner_path'))
        yaml_dict = {
            'paths': [{'file': '.\\Titanic2.csv'}, {'file': '..\\Titanic2.csv'}],
            'transformations': [{
                'read_delimited': {
                    'delimiter': ',', 'encoding': 'ascii', 'empty_as_string': False}}
            ]
        }

        exp_paths = ['file://' + os.path.normpath(os.path.join(base_path, 'Titanic2.csv')),
                     'file://' + os.path.normpath(os.path.join(base_path, '..\\Titanic2.csv'))]

        yaml_with_absolute_paths, _ = _make_all_paths_absolute(yaml_dict, base_path)
        for path_dict, exp_path in zip(yaml_with_absolute_paths['paths'], exp_paths):
            for _, path in path_dict.items():
                assert path == exp_path

    def test_make_all_paths_absolute_local_relative_path_no_initial_separator(
            self, get_data_folder_path):

        # Testing mixed windows/unix irregular relative path
        base_path = os.path.join(get_data_folder_path, 'dummy_basepath')
        yaml_dict = {
            'paths': [{'file': 'Titanic2.csv'}, {'file': 'subfolder\\Titanic2.csv'}],
            'transformations': [{
                'read_delimited': {
                    'delimiter': ',', 'encoding': 'ascii', 'empty_as_string': False}}
            ]
        }
        exp_paths = ['file://' + os.path.join(base_path, 'Titanic2.csv'),
                     'file://' + os.path.join(base_path, 'subfolder\\Titanic2.csv')]

        yaml_with_absolute_paths, _ = _make_all_paths_absolute(yaml_dict, base_path)
        for path_dict, exp_path in zip(yaml_with_absolute_paths['paths'], exp_paths):
            for _, path in path_dict.items():
                assert path == exp_path

    def test_make_all_paths_absolute_prior_loaded_local_path_with_diff_directory(self):
        mltable_yaml_dict = {'paths': [{'file': 'file://C:\\example\\test_data.csv'}]}
        new_base_dirc = 'C:\\example_new'
        result, _ = _make_all_paths_absolute(mltable_yaml_dict, new_base_dirc)
        assert result == mltable_yaml_dict
