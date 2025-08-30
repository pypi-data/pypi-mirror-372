import tempfile
import os
import shutil

from azureml.dataprep import UserErrorException
import pytest
from azureml.dataprep.api.mltable._mltable_helper import _read_yaml

from mltable.mltable import load, from_paths
from .helper_functions import mltable_as_dict, save_mltable_yaml_dict, list_of_dicts_equal, get_mltable_and_dicts


@pytest.mark.mltable_sdk_unit_test
class TestMLTableSave:
    def test_save_mltable_file_only_with_relative_paths(self, get_mltable_data_folder_path):
        mltable_path = get_mltable_data_folder_path
        og_mltable = load(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            og_mltable.save(td)
            og_mltable_yaml_dict = og_mltable._to_yaml_dict()
            saved_mltable_yaml_file_dict = _read_yaml(td)

            # paths in MLTable's Dataflow are saved as expected
            for path_dict in og_mltable_yaml_dict['paths']:
                for path_prop, path in path_dict.items():
                    path = path[7:]  # remove 'file://'
                    assert os.path.isabs(path)  # paths are saved to non-relative directory so saved as absolute paths
                    assert {path_prop: path} in saved_mltable_yaml_file_dict['paths']
                    assert os.path.exists(path)

    def test_save_mltable_only_to_relative_directory(self, get_mltable_data_folder_path):
        # mock saving MLTable to adjacent directory
        mltable_path = get_mltable_data_folder_path
        mltable_yaml_dict = _read_yaml(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            a_dirc = os.path.join(td, 'a')
            os.mkdir(a_dirc)

            b_dirc = os.path.join(td, 'b')
            os.mkdir(b_dirc)

            # set up fake MLTable file
            save_mltable_yaml_dict(a_dirc, mltable_yaml_dict)
            og_mltable = load(a_dirc)
            og_mltable.save(b_dirc)

            og_mltable_yaml_dict = mltable_as_dict(og_mltable)
            saved_mltable_yaml_file_dict = _read_yaml(b_dirc)

            # paths in MLTable's Dataflow are saved as expected
            for path_dict in og_mltable_yaml_dict['paths']:
                for path_prop, path in path_dict.items():
                    path = path[7:]  # remove 'file://'

                    # paths in MLTable's Dataflow are absolute
                    assert os.path.isabs(path)

                    # MLTable is saved to relative adjacent directory, so paths are saved as relative
                    path = os.path.relpath(path, b_dirc)
                    assert not os.path.isabs(path)
                    assert {path_prop: path} in saved_mltable_yaml_file_dict['paths']

    def test_save_mltable_only_to_existing_dirc_with_mltable_overwrite_true(self, get_mltable):
        mltable = get_mltable
        with tempfile.TemporaryDirectory() as save_dirc:
            save_path = os.path.join(save_dirc, 'MLTable')

            mltable.save(save_dirc)
            assert os.path.exists(save_path)

            mltable.save(save_dirc, colocated=False, overwrite=True, if_err_remove_files=False)
            assert os.path.exists(save_path)

    def test_save_to_existing_dirc_with_mltable_overwrite_false(self, get_mltable_data_folder_path):
        # try to save to directory that has a MLTable file
        # in this case the same directory the MLTable was originally loaded
        mltable_path = get_mltable_data_folder_path
        existing_mltable_save_path = os.path.join(mltable_path, 'MLTable')
        assert os.path.exists(existing_mltable_save_path)
        mltable = load(mltable_path)
        with pytest.raises(UserErrorException):
            mltable.save(mltable_path, overwrite=False, if_err_remove_files=False)
            # TODO right error code

    def test_save_to_file_path(self, get_mltable):
        # try to save to *existing* file path
        mltable = get_mltable
        with tempfile.TemporaryDirectory() as save_dirc:
            save_path = os.path.join(save_dirc, 'foo.yml')
            assert not os.path.exists(save_path)
            with open(save_path, 'w') as f:
                f.write('foo')
            assert os.path.isfile(save_path)

            with pytest.raises(UserErrorException):
                mltable.save(save_path)
                # TODO right error code

    def test_save_relative_to_non_colocated_directory_then_load(self, get_data_folder_path):
        mltable_dirc_path = os.path.join(get_data_folder_path, 'mltable_paths')
        mltable = load(mltable_dirc_path)

        with tempfile.TemporaryDirectory() as td:
            mltable.save(td, colocated=False)
            new_mltable, new_mltable_yaml_dict, new_mltable_yaml_file_dict = get_mltable_and_dicts(td)
            abs_relative_save_path = os.path.join(mltable_dirc_path, os.path.join('subfolder', 'Titanic2.csv'))
            abs_save_path = os.path.splitdrive(get_data_folder_path)[0] + os.path.normpath('/this/is/a/fake/path.csv')

            # paths after saving but before loading
            # saved paths & loaded path attributes are the same
            list_of_dicts_equal([{'file': abs_save_path}, {'file': abs_relative_save_path}],
                                new_mltable_yaml_file_dict['paths'],
                                new_mltable.paths)

            # paths after being loaded to MLTable's Dataflow, only change is `file://` is prepended to each path
            list_of_dicts_equal([{k: 'file://' + v for k, v in path_dict.items()}
                                for path_dict in new_mltable_yaml_file_dict['paths']],
                                new_mltable_yaml_dict['paths'])

    def test_save_relative_to_colocated_directory_then_load(self):
        with tempfile.TemporaryDirectory() as td:
            a_dirc = os.path.join(td, 'a')
            os.mkdir(a_dirc)

            b_dirc = os.path.join(td, 'b')
            os.mkdir(b_dirc)

            dirc_mount = os.path.splitdrive(os.getcwd())[0]

            # enter the "relative path" as absolute
            abs_paths = [{'file': dirc_mount + os.path.normpath('/this/is/absolute/path.csv')},
                         {'file': os.path.normpath(os.path.join(a_dirc, 'this/is/relative/path.csv'))}]
            rel_paths = [{'file': dirc_mount + os.path.normpath('/this/is/absolute/path.csv')},
                         {'file': os.path.normpath('this/is/relative/path.csv')}]

            mltable = from_paths(abs_paths)

            # save & load initial MLTable
            mltable.save(a_dirc, colocated=False)
            loaded_mltable = load(a_dirc)
            loaded_mltable, loaded_mltable_yaml_dict, loaded_mltable_yaml_file_dict \
                = get_mltable_and_dicts(a_dirc)

            # paths in MLTable's Dataflow after loading
            loaded_paths = [{k : 'file://' + v for k, v in path_dict.items()} for path_dict in abs_paths]
            list_of_dicts_equal(loaded_paths, loaded_mltable_yaml_dict['paths'])

            # paths are same before & after loading
            list_of_dicts_equal(rel_paths, loaded_mltable.paths, loaded_mltable_yaml_file_dict['paths'])

            # save to adjacent directory & reload
            loaded_mltable.save(b_dirc, colocated=False)
            reloaded_mltable, reloaded_mltable_yaml_dict, reloaded_mltable_yaml_file_dict \
                = get_mltable_and_dicts(b_dirc)

            # after resaving & reloading absolute paths are same but relative paths are adjusted
            reloaded_mltable_paths = [{k: v if os.path.isabs(v) else os.path.relpath(os.path.join(a_dirc, v), b_dirc)
                                      for k, v in path_dict.items()} for path_dict in rel_paths]
            list_of_dicts_equal(reloaded_mltable.paths,
                                reloaded_mltable_paths,
                                reloaded_mltable_yaml_file_dict['paths'])

            # absolute paths are kept consistent across two sequentiual loads
            list_of_dicts_equal(loaded_mltable_yaml_dict['paths'], reloaded_mltable_yaml_dict['paths'])

    def test_save_load_dataframe(self, get_mltable_data_folder_path):
        with tempfile.TemporaryDirectory() as td:
            a_dirc = os.path.join(td, 'a')
            b_dirc = os.path.join(td, 'b')

            # copy MLTable file & data files
            shutil.copytree(get_mltable_data_folder_path, a_dirc)

            og_mltable = load(a_dirc)
            og_dataframe = og_mltable.to_pandas_dataframe()
            og_mltable.save(b_dirc, colocated=False)

            loaded_mltable, _, loaded_mltable_yaml_file_dict = get_mltable_and_dicts(b_dirc)

            # loaded paths are relative
            for path_dict in loaded_mltable_yaml_file_dict['paths']:
                assert all(not os.path.isabs(path) for _, path in path_dict.items())

            loaded_dataframe = loaded_mltable.to_pandas_dataframe()

            assert og_dataframe is not None
            assert not og_dataframe.empty
            assert og_dataframe.equals(loaded_dataframe)


@pytest.mark.mltable_sdk_unit_test_windows
class TestMLTableSaveWindowsOnly:
    def test_save_diff_mount(self, get_data_folder_path):
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows')
        og_mltable = load(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            og_mltable.save(td)
            og_mltable_yaml_dict = mltable_as_dict(og_mltable)
            saved_mltable_yaml_file_dict = _read_yaml(td)

            # original MLTable directory & save directory are on different mounts
            dirc_mount = os.path.splitdrive(td)[0]
            for path_dirc in og_mltable_yaml_dict['paths']:
                assert os.path.splitdrive(path_dirc['file'])[0] != dirc_mount

            # all paths are absolute paths whose mount in the original MLTable direcotry
            exp_save_paths = [{'file': 'D:\\absolute\\path\\file.csv'},
                              {'file': os.path.join(mltable_path, 'relative\\path\\file.csv')}]

            # explit check that saved paths are the same
            list_of_dicts_equal(exp_save_paths, saved_mltable_yaml_file_dict['paths'])

    def test_save_same_mount(self, get_data_folder_path):
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows_c_drive')
        mltable_yaml_dirc = _read_yaml(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            a_dirc = os.path.join(td, 'a')
            os.mkdir(a_dirc)

            b_dirc = os.path.join(td, 'b')
            os.mkdir(b_dirc)

            # setup fake MLTable
            save_mltable_yaml_dict(a_dirc, mltable_yaml_dirc)
            og_mltable = load(a_dirc)
            og_mltable.save(b_dirc)

            og_mltable_yaml_dict = mltable_as_dict(og_mltable)
            saved_mltable_yaml_file_dict = _read_yaml(b_dirc)

            # original MLTable directory & save directory are on same mounts
            dirc_mount = os.path.splitdrive(td)[0]
            for path_dirc in og_mltable_yaml_dict['paths']:
                if os.path.isabs(path_dirc['file']):
                    assert os.path.splitdrive(path_dirc['file'])[0] == dirc_mount

            exp_save_paths = [{'file': os.path.relpath('C:\\absolute\\path\\file.csv', b_dirc)},
                              {'file': '..\\a\\relative\\path\\file.csv'}]

            # explit check that saved paths are the same
            list_of_dicts_equal(exp_save_paths, saved_mltable_yaml_file_dict['paths'])


@pytest.mark.mltable_sdk_unit_test_windows
class TestMLTableSaveAndLoadWindowsOnly:
    def test_load_save_diff_drive(self, get_data_folder_path):
        # all files on loaded MLTable are on on D drive / mount, save to C drive / mount (temp directory)
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows')
        og_mltable = load(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            og_mltable.save(td, colocated=False)
            new_mltable, new_mltable_yaml_dict, new_mltable_yaml_file_dict = get_mltable_and_dicts(td)
            relative_file_save_path = os.path.join(mltable_path, 'relative\\path\\file.csv')

            # explit check for paths after saving but before loading
            # paths are same before & after loading
            list_of_dicts_equal([{'file': 'D:\\absolute\\path\\file.csv'}, {'file': relative_file_save_path}],
                                new_mltable_yaml_file_dict['paths'],
                                new_mltable.paths)

            # explicit check for paths after loading
            list_of_dicts_equal([{'file': 'file://D:\\absolute\\path\\file.csv'},
                                 {'file': 'file://' + relative_file_save_path}],
                                new_mltable_yaml_dict['paths'])

    def test_load_save_same_drive(self, get_data_folder_path):
        # absolute file in loaded MLTable is on C drive / mount, save to C drive / mount (temp directory)
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows_c_drive')
        og_mltable = load(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            og_mltable.save(td, colocated=False)
            new_mltable, new_mltable_yaml_dict, new_mltable_yaml_file_dict = get_mltable_and_dicts(td)
            relative_file_save_path = os.path.join(mltable_path, 'relative\\path\\file.csv')
            absolute_file_save_path = os.path.relpath('C:\\absolute\\path\\file.csv', td)

            # explicit ceheck for paths after saving but before loading
            # paths are same before & after loading
            list_of_dicts_equal([{'file': absolute_file_save_path}, {'file': relative_file_save_path}],
                                new_mltable_yaml_file_dict['paths'],
                                new_mltable.paths)

            # explicit check for paths after reloading
            list_of_dicts_equal([{'file': 'file://C:\\absolute\\path\\file.csv'},
                                 {'file': 'file://' + relative_file_save_path}],
                                new_mltable_yaml_dict['paths'])
