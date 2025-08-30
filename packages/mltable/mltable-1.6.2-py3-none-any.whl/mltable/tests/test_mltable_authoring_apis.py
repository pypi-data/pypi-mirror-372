import os
import tempfile
import shutil

import pytest
import yaml
from azureml.dataprep import UserErrorException

from mltable.mltable import load, from_delimited_files, from_parquet_files, from_json_lines_files, from_paths
from .helper_functions import mltable_as_dict, list_of_dicts_equal, get_mltable_and_dicts


@pytest.mark.mltable_sdk_unit_test
class TestMLTableMiscTransformations:
    @pytest.mark.parametrize('cols_to_drop', ['Name',                     # single string column
                                              'laptop',                   # non-existant column
                                              ['Name'],                   # single column list
                                              ["Name", "Age"],            # multiple columns
                                              ["Name", "Age", "laptop"],  # non-existant column
                                              [],                         # empty
                                              ("Name", "Age"),            # as tuple
                                              {"Name", "Age"}])          # as set
    def test_drop(self, get_mltable_with_type, cols_to_drop):
        try:
            wrapped_cols_to_drop = [cols_to_drop] if isinstance(cols_to_drop, str) else cols_to_drop
            present_columns \
                = set(get_mltable_with_type.to_pandas_dataframe().columns).intersection(wrapped_cols_to_drop)
            post_drop_columns = set(get_mltable_with_type.drop_columns(cols_to_drop).to_pandas_dataframe().columns)

            # columns present before that were suppose to be dropped are dropped
            assert post_drop_columns.isdisjoint(present_columns)

            # sanity check for when non-existant columns are "dropped"
            assert post_drop_columns.isdisjoint(wrapped_cols_to_drop)
        except UserErrorException as e:
            # TODO (nathof) released version of dprep has behavior we are reverting, remove fallback after release
            if 'expected Multi selector can not be empty' in str(e) and cols_to_drop == []:
                pass
            else:
                raise e

    @pytest.mark.parametrize('cols_to_drop', [["Age", "Name", "Age"], ('Name', 'Age', 'Name')])
    def test_drop_dup_cols(self, get_mltable_with_type, cols_to_drop):
        with pytest.raises(UserErrorException, match='Found duplicate columns in given column names:.*'):
            get_mltable_with_type.drop_columns(cols_to_drop)

    @pytest.mark.parametrize('columns', ['datetime', ["datetime", "index"]])
    def test_try_drop_traits(self, get_trait_timestamp_mltable, columns):
        assert "datetime" == get_trait_timestamp_mltable.traits.timestamp_column
        assert "datetime" == get_trait_timestamp_mltable.traits.index_columns[0]

        with pytest.raises(UserErrorException, match='Columns in traits must be kept and cannot be dropped'):
            get_trait_timestamp_mltable.drop_columns(columns=columns)

    @pytest.mark.parametrize('cols_to_keep', ['Name',                     # single string column
                                              ['Name'],                   # single column list
                                              ["Name", "Age"],            # multiple columns
                                              ("Name", "Age"),            # as tuple
                                              {"Name", "Age"}])           # as set
    def test_keep(self, get_mltable_with_type, cols_to_keep):
        wrapped_cols_to_keep = [cols_to_keep] if isinstance(cols_to_keep, str) else cols_to_keep
        existing_columns = set(get_mltable_with_type.to_pandas_dataframe().columns)
        present_columns = existing_columns.intersection(wrapped_cols_to_keep)
        post_keep_columns = set(get_mltable_with_type.keep_columns(cols_to_keep).to_pandas_dataframe().columns)

        # columns present before are only columns left
        assert post_keep_columns == present_columns

        # sanity check that columns to be "dropped" that aren't present before are not present after
        assert all(col not in post_keep_columns for col in wrapped_cols_to_keep if col not in existing_columns)

    @pytest.mark.parametrize('cols_to_keep', [["Age", "Name", "Age"], ('Name', 'Age', 'Name')])
    def test_keep_dup_cols(self, get_mltable_with_type, cols_to_keep):
        with pytest.raises(UserErrorException, match='Found duplicate columns in given column names:.*'):
            get_mltable_with_type.keep_columns(cols_to_keep)

    def test_keep_columns_with_trait_trait_not_given(self, get_trait_timestamp_mltable):
        assert "elevation" != get_trait_timestamp_mltable.traits.timestamp_column
        assert "elevation" != get_trait_timestamp_mltable.traits.index_columns[0]
        assert "datetime" == get_trait_timestamp_mltable.traits.timestamp_column
        assert "datetime" == get_trait_timestamp_mltable.traits.index_columns[0]

        with pytest.raises(UserErrorException, match='Columns in traits must be kept and cannot be dropped'):
            get_trait_timestamp_mltable.keep_columns(columns="elevation")

    def test_traits_from_mltable_file(self, get_trait_timestamp_mltable):
        mltable = get_trait_timestamp_mltable

        mltable_yaml = yaml.safe_load(mltable._dataflow.to_yaml_string())
        assert mltable.traits.timestamp_column == 'datetime'
        assert mltable.traits.index_columns == ['datetime']
        assert mltable_yaml['traits']['index_columns'] == ['datetime']

        mltable.traits.timestamp_column = 'random_column_name'
        mltable_yaml = yaml.safe_load(mltable._dataflow.to_yaml_string())
        assert mltable.traits.timestamp_column == 'random_column_name'
        assert mltable_yaml['traits']['timestamp_column'] == 'random_column_name'

        mltable.traits.index_columns = ['col1', 'col2']
        mltable_yaml = yaml.safe_load(mltable._dataflow.to_yaml_string())
        assert mltable.traits.index_columns == ['col1', 'col2']
        assert mltable_yaml['traits']['index_columns'] == ['col1', 'col2']

    def test_set_get_traits(self, get_mltable):
        mltable = get_mltable
        mltable.traits.index_columns = ['PassengerId']
        mltable.traits.timestamp_column = 'Pclass'
        assert mltable.traits.index_columns == ['PassengerId']
        assert mltable.traits.timestamp_column == 'Pclass'

    def test_take(self, get_mltable):
        mltable = get_mltable
        new_mltable = mltable.take(count=5)

        assert '- take: 5' in new_mltable._dataflow.to_yaml_string()
        df = new_mltable.to_pandas_dataframe()
        assert df.shape[0] == 5

    def test_take_invalid_count(self, get_mltable):
        for invalid in -1, 0, "number":
            with pytest.raises(UserErrorException, match='Number of rows must be a positive integer'):
                get_mltable.take(count=invalid)

    def test_show(self, get_mltable):
        mltable = get_mltable
        new_mltable = mltable.show(count=5)
        assert new_mltable.shape[0] == 5

    def test_show_invalid_count(self, get_mltable):
        for invalid in -1, 0, "number":
            with pytest.raises(UserErrorException, match='Number of rows must be a positive integer'):
                get_mltable.show(count=invalid)

    @pytest.mark.parametrize('probability', [.05, .1, .3])
    @pytest.mark.parametrize('seed', [None, 5, 100])
    def test_take_random_sample(self, get_mltable, probability, seed):
        # just need to assert that it can load a dataframe of any size (even empty)
        get_mltable.take_random_sample(probability, seed).to_pandas_dataframe()

    @pytest.mark.parametrize('probability', [-.01, 0.0, 'number', 2])
    def test_take_random_sample_invalid_prob(self, get_mltable, probability):
        with pytest.raises(UserErrorException, match='Probability should an float greater than 0 and less than 1'):
            get_mltable.take_random_sample(probability)

    @pytest.mark.parametrize('idx', [0, -1])
    def test_add_step_at_start(self, get_mltable, idx):
        mltable = get_mltable
        mltable_info_dict = mltable_as_dict(mltable)
        added_transformations = mltable_info_dict['transformations']

        # only one transformation added
        assert len(added_transformations) == 1
        assert list(added_transformations[0].keys())[0] == 'read_delimited'

        # add `take 5` step, if `idx` is `None` resort to default arg (also `None`)
        take_dataflow = mltable._dataflow.add_transformation('take', 5, idx)
        added_transformations = yaml.safe_load(take_dataflow.to_yaml_string())['transformations']

        # two transformations added, `take 5` at end
        assert len(added_transformations) == 2
        assert added_transformations[0] == {'take': 5}

    @pytest.mark.parametrize('idx', [None, 1])
    def test_add_step_at_end(self, get_mltable, idx):
        mltable = get_mltable
        mltable_info_dict = mltable_as_dict(mltable)
        added_transformations = mltable_info_dict['transformations']

        # only one transformation added
        assert len(added_transformations) == 1
        assert list(added_transformations[0].keys())[0] == 'read_delimited'

        # add `take 5` step to end
        if idx is None:
            take_dataflow = mltable._dataflow.add_transformation('take', 5)
        else:
            take_dataflow = mltable._dataflow.add_transformation(
                'take', 5, idx)
        added_transformations = yaml.safe_load(take_dataflow.to_yaml_string())[
            'transformations']

        # two transformations added, `take 5` at end
        assert len(added_transformations) == 2
        assert added_transformations[-1] == {'take': 5}

    def test_add_mult_steps(self, get_mltable):
        mltable = get_mltable
        mltable_info_dict = mltable_as_dict(mltable)
        added_transformations = mltable_info_dict['transformations']

        # only one transformation added
        assert len(added_transformations) == 1
        assert list(added_transformations[0].keys())[0] == 'read_delimited'

        # add `take 10` step
        mltable = mltable.take(10)
        mltable_info_dict = mltable_as_dict(mltable)
        added_transformations = mltable_info_dict['transformations']

        # two transformations added, `take 10` at end
        assert len(added_transformations) == 2
        assert added_transformations[-1] == {'take': 10}

        # add `take 20` step to the middle
        take_dataflow = mltable._dataflow.add_transformation('take', 20, -1)
        added_transformations = yaml.safe_load(take_dataflow.to_yaml_string())[
            'transformations']

        # three transformation steps added, `take 20` in middle and `take 10` at end
        assert len(added_transformations) == 3
        assert added_transformations[-2] == {'take': 20}
        assert added_transformations[-1] == {'take': 10}

    @pytest.mark.parametrize('percent', [.5, .7])
    def test_random_split(self, get_mltable, percent):
        mltable = get_mltable.take(20)
        a, b = mltable.random_split(percent=percent, seed=10)

        a = a.to_pandas_dataframe()
        b = b.to_pandas_dataframe()
        c = mltable.to_pandas_dataframe()

        bound = .2
        # assert a have ~`percent`% of c's data
        assert abs(percent - (len(a) / len(c))) <= bound

        # assert has ~(1 - `percent`)% (the remainder) of c's data
        assert abs((1 - percent) - (len(b) / len(c))) <= bound

        # assert the number of elements in a and b equals c
        assert (len(a) + len(b)) == len(c)

        # show a & b are both in c
        assert c.merge(a).equals(a)
        assert c.merge(b).equals(b)

        # assert a and b have no overlap
        assert a.merge(b).empty

    def test_get_partition_count(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_delimited_files(paths)
        assert mltable.get_partition_count() == 1

        mltable = mltable._with_partition_size(200)
        assert mltable.get_partition_count() == 11

        # with partition_size unit
        mltable = mltable._with_partition_size(500, 'kb')
        assert mltable.get_partition_count() == 1

    def test_update_partition_size_with_parquet(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime.parquet'}]
        mltable = from_parquet_files(paths)
        exp_err_msg = 'transformation step read_delimited or read_json_lines is required to update partition_size'
        with pytest.raises(UserErrorException) as e:
            mltable._with_partition_size(partition_size=200)
            assert exp_err_msg in e.message

    def test_mltable_from_delimited_files_is_tabular(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_delimited_files(paths)
        assert mltable._is_tabular

    def test_mltable_from_parquet_is_tabular(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime.parquet'}]
        mltable = from_parquet_files(paths)
        assert mltable._is_tabular

    def test_mltable_from_json_files_is_tabular(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/order.jsonl'}]
        mltable = from_json_lines_files(paths)
        assert mltable._is_tabular

    def test_mltable_load_is_tabular(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        test_mltable_dir = os.path.join(
            cwd, 'data/mltable/mltable_file')
        mltable = load(test_mltable_dir)
        assert not mltable._is_tabular

    def test_save_relative_to_non_colocated_directory_then_load(self, get_data_folder_path):
        mltable_dirc_path = os.path.join(get_data_folder_path, 'mltable_paths')
        mltable = load(mltable_dirc_path)

        with tempfile.TemporaryDirectory() as td:
            mltable.save(td)
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
            mltable.save(a_dirc)
            loaded_mltable = load(a_dirc)
            loaded_mltable, loaded_mltable_yaml_dict, loaded_mltable_yaml_file_dict \
                = get_mltable_and_dicts(a_dirc)

            # paths in MLTable's Dataflow after loading
            loaded_paths = [{k : 'file://' + v for k, v in path_dict.items()} for path_dict in abs_paths]
            list_of_dicts_equal(loaded_paths, loaded_mltable_yaml_dict['paths'])

            # paths are same before & after loading
            list_of_dicts_equal(rel_paths, loaded_mltable.paths, loaded_mltable_yaml_file_dict['paths'])

            # save to adjacent directory & reload
            loaded_mltable.save(b_dirc)
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
            og_mltable.save(b_dirc)

            loaded_mltable, _, loaded_mltable_yaml_file_dict = get_mltable_and_dicts(b_dirc)

            # loaded paths are relative
            for path_dict in loaded_mltable_yaml_file_dict['paths']:
                assert all(not os.path.isabs(path) for _, path in path_dict.items())

            loaded_dataframe = loaded_mltable.to_pandas_dataframe()

            assert og_dataframe is not None
            assert not og_dataframe.empty
            assert og_dataframe.equals(loaded_dataframe)


@pytest.mark.mltable_sdk_unit_test_windows
class TestMLTableSaveAndLoadWindowsOnly:
    def test_load_save_diff_drive(self, get_data_folder_path):
        # all files on loaded MLTable are on on D drive / mount, save to C drive / mount (temp directory)
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows')
        og_mltable = load(mltable_path)

        with tempfile.TemporaryDirectory() as td:
            og_mltable.save(td)
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
            og_mltable.save(td)
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
