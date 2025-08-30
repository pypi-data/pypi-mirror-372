import os

import pytest
from azureml.dataprep import UserErrorException

from mltable.mltable import load, from_delimited_files, DataType, MLTableHeaders
from .helper_functions import mltable_was_loaded


@pytest.mark.mltable_sdk_unit_test
class TestFromDelimitedFiles:

    def test_create_mltable_from_delimited_files_with_local_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'}]
        mltable = from_delimited_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (10, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_from_delimited_files_with_local_paths(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'},
                 {'file': 'data/crime-winter.csv'}]
        mltable = from_delimited_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_from_delimited_files_with_folder_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'folder': 'data/mltable/mltable_folder'}]
        mltable = from_delimited_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_from_delimited_files_with_local_abs_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_delimited_files(paths)
        df = mltable_was_loaded(mltable)
        assert df.shape == (10, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_from_delimited_files_with_header_enum(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'},
                 {'file': 'data/crime-winter.csv'}]
        mltable = from_delimited_files(
            paths, header=MLTableHeaders.all_files_same_headers)
        df = mltable_was_loaded(mltable)
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_create_mltable_from_delimited_files_with_header_no_string(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'},
                 {'file': 'data/crime-winter.csv'}]
        with pytest.raises(UserErrorException, match='The header should be a string or an MLTableHeader enum'):
            from_delimited_files(paths, header=1)

    def test_all_file_same_header(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/crime-spring.csv'},
                 {'file': 'data/crime-winter.csv'}]
        mltable = from_delimited_files(paths, header='all_files_same_headers')
        df = mltable.to_pandas_dataframe()
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_no_header(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(os.path.join(
            cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_delimited_files(paths, header='no_header')
        df = mltable.to_pandas_dataframe()
        assert df.shape == (11, 22)

    def test_with_auto_type_conversion_incorrect_type(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        with pytest.raises(UserErrorException, match='`infer_column_types` must be a bool or a dictionary.'):
            from_delimited_files(paths, infer_column_types=5)

    def test_with_auto_type_conversion_extraneous_keys(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = 'If `infer_column_types` is a dictionary, may only contain keys ' \
                      '`sample_size` and `column_type_overrides`.'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'some-key': 5})

    def test_with_auto_type_conversion_incorrect_sample_size(self, get_dataset_data_folder_path):
        for sample_size in '5', -2, 0:
            dirc = get_dataset_data_folder_path
            paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
            exp_err_msg = 'If `infer_column_types` is a dictionary with a `sample_size` key, its value must be a ' \
                          'positive integer.'
            with pytest.raises(UserErrorException, match=exp_err_msg):
                from_delimited_files(paths, infer_column_types={'sample_size': sample_size})

    def test_with_auto_type_conversion_column_type_overrides_unsupported_value_type(
            self, get_dataset_data_folder_path):

        for sample_size in '5', -2, 0:
            dirc = get_dataset_data_folder_path
            paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
            exp_err_msg = f"'{sample_size}' is not a supported string conversion for `mltable.DataType`, " \
                          "supported types are 'string', 'int', 'float', 'boolean', & 'stream_info'"
            with pytest.raises(UserErrorException, match=exp_err_msg):
                from_delimited_files(paths, infer_column_types={'column_type_overrides': {'foo': sample_size}})

    def test_with_auto_type_conversion_column_type_overrides_unsupported_string(
            self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = "'datetime' is not a supported string conversion for `mltable.DataType`, " \
                      "supported types are 'string', 'int', 'float', 'boolean', & 'stream_info'"
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'column_type_overrides': {'foo': 'datetime'}})

    def test_with_auto_type_conversion_column_type_overrides_stream_type(
            self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = 'Type overrides to stream are not supported, try mltable.MLTable.convert_column_types instead'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'column_type_overrides': {'foo': DataType.to_stream()}})

    def test_with_auto_type_conversion_column_type_overrides_stream_type_string(
            self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = 'Type overrides to stream are not supported, try mltable.MLTable.convert_column_types instead'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'column_type_overrides': {'foo': 'stream_info'}})

    def test_with_auto_type_conversion_incorrect_column_type_overrides_type(
            self, get_dataset_data_folder_path):

        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = 'If `infer_column_types` is a dictionary with a `column_type_overrides` key, ' \
                      'its value must be a dictionary of strings to `mltable.DataType`s or strings.'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'column_type_overrides': '5'})

    def test_with_auto_type_conversion_true(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types=True)
        df = mltable.to_pandas_dataframe()
        assert list(map(str, df.dtypes)) == ['int64', 'object', 'datetime64[ns]', 'object', 'int64', 'object',
                                             'object', 'object', 'bool', 'bool', 'int64', 'int64', 'int64', 'int64',
                                             'int64', 'float64', 'float64', 'int64', 'datetime64[ns]', 'float64',
                                             'float64', 'object']

    def test_with_auto_type_conversion_false(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types=False)
        df = mltable.to_pandas_dataframe()
        # object is Pandas's data type for a string, all are strings
        all(x == 'object' for x in map(str, df.dtypes))

    def test_with_auto_type_conversion_overrides(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]

        # before conversion
        mltable = from_delimited_files(paths, infer_column_types=True)
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'int64'

        # after conversion
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types={'sample_size': 5,
                                                                  'column_type_overrides': {
                                                                      'ID': DataType.to_float()
                                                                  }})
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'float64'

    def test_with_auto_type_conversion_overrides_from_false(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]

        # before conversion
        mltable = from_delimited_files(paths, infer_column_types=False)
        df = mltable.to_pandas_dataframe()
        assert all(x == 'object' for x in map(str, df.dtypes))

        # after conversion
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types={'sample_size': 5,
                                                                  'column_type_overrides': {
                                                                      'ID': 'float',
                                                                      'Date': DataType.to_datetime('%m/%d/%Y %H:%M'),
                                                                      'Domestic': DataType.to_bool(['TRUE'], ['FALSE'],
                                                                                                   'false')
                                                                  }})
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'float64'
        assert str(df['Date'].dtype) == 'datetime64[ns]'
        assert str(df['Domestic'].dtype) == 'bool'

    def test_with_auto_type_conversion_multi_override(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]

        # before conversion
        mltable = from_delimited_files(paths, infer_column_types=False)
        df = mltable.to_pandas_dataframe()
        assert all(x == 'object' for x in map(str, df.dtypes))

        # after conversion
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types={'sample_size': 5,
                                                                  'column_type_overrides': {
                                                                      ('Date', 'ID'): 'string'
                                                                  }})
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'object'
        assert str(df['Date'].dtype) == 'object'

    def test_with_auto_type_conversion_incorrect_keys(self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = \
            'If `infer_column_types` is a dictionary, may only contain keys `sample_size` and `column_type_overrides`.'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'sample_size': 200, 'ID': 'int'})

    def test_with_auto_type_conversion_dup_col_overrides_both_single_gives_last_type(
            self, get_dataset_data_folder_path):

        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(dirc, 'crime-spring.csv'))}]
        mltable = from_delimited_files(paths, infer_column_types={'column_type_overrides': {
            'ID': DataType.to_float(),  # noqa: F601
            'ID': DataType.to_int()  # noqa: F601
        }})
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'int64'

    def test_with_auto_type_conversion_dup_col_overrides_multi_and_single(
            self, get_dataset_data_folder_path):
        dirc = get_dataset_data_folder_path
        paths = [{'file': os.path.normpath(os.path.join(dirc, 'crime-spring.csv'))}]
        exp_err_msg = "Found duplicate column. Cannot convert column 'ID' to multiple `mltable.DataType`s."
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, infer_column_types={'column_type_overrides': {
                'ID': DataType.to_float(),
                ('ID', 'Latitude'): DataType.to_float()
            }})

    def test_with_auto_type_conversion_true_yaml(self, get_data_folder_path):
        dirc = get_data_folder_path
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_true')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        assert list(map(str, df.dtypes)) == ['int64', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
                                             'float64', 'float64', 'float64', 'object', 'object', 'int64', 'int64',
                                             'datetime64[ns]', 'datetime64[ns]', 'bool', 'object']

    def test_with_auto_type_conversion_false_yaml(self, get_data_folder_path):
        dirc = get_data_folder_path
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_false')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        # object is Pandas's data type for a string, all are strings
        assert all(x == 'object' for x in map(str, df.dtypes))

    def test_auto_type_conversion_multi_column_overrides_yaml(self, get_data_folder_path):
        dirc = get_data_folder_path

        # before conversion
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_true')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        assert str(df['datetime'].dtype) == 'datetime64[ns]'
        assert str(df['date'].dtype) == 'datetime64[ns]'

        # after conversion
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_multi_overrides')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        assert str(df['datetime'].dtype) == 'object'
        assert str(df['date'].dtype) == 'object'

    def test_auto_type_conversion_overrides_yaml_from_strings(self, get_data_folder_path):
        dirc = get_data_folder_path

        # before conversion
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_false')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        assert all(x == 'object' for x in map(str, df.dtypes))

        # after conversion
        mltable_yaml_path = os.path.join(
            dirc, 'mltable_from_delimited/with_overrides')
        mltable = load(mltable_yaml_path)
        df = mltable.to_pandas_dataframe()
        assert str(df['ID'].dtype) == 'float64'

    def test_with_auto_type_conversion_malformed_overrides_yaml(self, get_data_folder_path):
        dirc = get_data_folder_path
        mltable_yaml_path = os.path.join(dirc, 'mltable_from_delimited/malformed_overrides')
        with pytest.raises(UserErrorException, match='Given MLTable does not adhere to the AzureML MLTable schema.*'):
            load(mltable_yaml_path)

    """
    this test case is tno working now. Need to clarify.
    def test_different_header(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/mltable/mltable_file_different_header/crime-spring.csv'},
                 {'file': 'data/mltable/mltable_file_different_header/crime-winter.csv'}]
        mltable = from_delimited_files(paths, header='all_files_different_headers')
        df = mltable.to_pandas_dataframe()
        assert df.shape == (20, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]
    """

    def test_header_from_first_file(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [{'file': 'data/mltable/mltable_file_different_header/crime-spring.csv'},
                 {'file': 'data/mltable/mltable_file_different_header/crime-winter.csv'}]
        mltable = from_delimited_files(paths, header='from_first_file')
        df = mltable.to_pandas_dataframe()
        assert df.shape == (21, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_unknown_header_option(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(os.path.join(cwd, 'data/crime-spring.csv'))
        paths = [{'file': exp_path_1}]
        exp_err_msg = "Given invalid header some_unknown_option, supported headers are: 'no_header', " \
                      "'from_first_file', 'all_files_different_headers', and 'all_files_same_headers'."
        with pytest.raises(UserErrorException, match=exp_err_msg):
            from_delimited_files(paths, header='some_unknown_option')

    def test_with_encoding(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/latin1encoding.csv'))
        paths = [{'file': exp_path_1}]
        mltable = from_delimited_files(paths, encoding='latin1')
        df = mltable_was_loaded(mltable)
        assert df.shape == (87, 66)

    @pytest.mark.skip(reason="Incorrect test, skip now before new version of dprep is released")
    def test_support_multi_line(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/multi_line_field.csv'))
        paths = [{'file': exp_path_1}]
        mltable_multi_line = from_delimited_files(
            paths, support_multi_line=True)
        df = mltable_multi_line.to_pandas_dataframe()
        assert df.shape == (2, 3)

    def test_empty_as_string(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        exp_path_1 = os.path.normpath(
            os.path.join(cwd, 'data/empty_fields.csv'))
        paths = [{'file': exp_path_1}]
        mltable_as_string = from_delimited_files(paths, empty_as_string=True)
        df_as_string = mltable_as_string.to_pandas_dataframe()
        assert df_as_string.shape == (2, 2)
        assert df_as_string['A'].values[0] == ""

    def test_create_mltable_from_delimited_files_delimiter_semicolon(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        paths = [{'file': os.path.normpath(
            os.path.join(cwd, 'data/mltable/mltable_different_delimiter/crime-spring-semicolon.csv'))}]
        # TODO default datetime forums if not provided?
        mltable = from_delimited_files(
            paths, delimiter=';', header='all_files_same_headers', infer_column_types=False)
        df = mltable_was_loaded(mltable)
        assert df.shape == (2, 22)
        assert list(df.columns) == [
            'ID', 'Case Number', 'Date', 'Block', 'IUCR', 'Primary Type', 'Description', 'Location Description',
            'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
            'Y Coordinate', 'Year', 'Updated On', 'Latitude', 'Longitude', 'Location'
        ]

    def test_check_path(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)
        paths = [
            {'pattern': 'data/mltable/mltable_file_different_header/*.csv'}]
        mltable = from_delimited_files(
            paths, header='all_files_different_headers')
        assert mltable.paths == [
            {'pattern': 'data/mltable/mltable_file_different_header/*.csv'}]
