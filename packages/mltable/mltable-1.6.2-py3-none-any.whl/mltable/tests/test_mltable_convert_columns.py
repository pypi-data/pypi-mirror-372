import os

import pytest
from azureml.dataprep import UserErrorException
from azureml.dataprep.native import StreamInfo
from mltable.mltable import load, DataType

from .helper_functions import _test_save_load_round_trip


@pytest.mark.mltable_sdk_unit_test
class TestMLTableDataType:
    def test_empty_datetime_formats(self):
        with pytest.raises(UserErrorException,
                           match="Expect `formats` to be a single string, a list of strings, or a tuple of strings"):
            DataType.to_datetime(formats=None)

    def test_boolean_bad_mismatch_as(self):
        # Using incorrect mismatch_as string
        with pytest.raises(UserErrorException, match='.*`mismatch_as` can only be.*'):
            DataType.to_bool(false_values=['0'], mismatch_as='dummyVar')

    @pytest.mark.parametrize('true_values,false_values', [([], ['0']), (['1'], []), (None, ['0']), (['1'], None)])
    def test_boolean_true_false_lengths_not_matching(self, true_values, false_values):
        with pytest.raises(UserErrorException,
                           match="`true_values` and `false_values` must both be None or non-empty list of strings"):
            DataType.to_bool(true_values=true_values, false_values=false_values)

    @pytest.mark.parametrize('true_values,false_values', [([5], ['0']), (['1'], [5.3])])
    def test_boolean_bad_true_false_values(self, true_values, false_values):
        with pytest.raises(UserErrorException,
                           match=".*must only consists of strings"):
            DataType.to_bool(true_values=true_values, false_values=false_values)

    @pytest.mark.parametrize('true_values,false_values', [(['1', 'True'], ['False', '1']),
                                                          (['1'], '1'),
                                                          ('0', ['0']),
                                                          ('1', '1')])
    def test_boolean_overlapping_values(self, true_values, false_values):
        with pytest.raises(UserErrorException,
                           match='`true_values` and `false_values` can not have overlapping values'):
            DataType.to_bool(true_values=true_values, false_values=false_values)


@pytest.mark.mltable_sdk_unit_test
class TestMLTableConvertColumnTypes:
    def assert_all_cols_are_object(self, mltable):
        assert all(col.name == 'object' for col in mltable.to_pandas_dataframe().dtypes)

    @pytest.mark.parametrize('formats', ['%Y-%m-%d %H:%M:%S',
                                         ['%Y-%m-%d %H:%M:%S'],
                                         ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']])
    def test_save_load_datetime_formats(self, get_mltable, formats):
        _test_save_load_round_trip(
            get_mltable.convert_column_types(column_types={'': DataType.to_datetime(formats=formats)}))

    def test_convert_simple_types_sdk(self, get_mltable_with_type):
        self.assert_all_cols_are_object(get_mltable_with_type)
        new_mltable = get_mltable_with_type.convert_column_types(column_types={'PassengerId': DataType.to_int(),
                                                                               'Fare': DataType.to_float(),
                                                                               'Pclass': 'int',
                                                                               'Ticket': 'string',
                                                                               'Survived': 'boolean'})

        new_column_types = new_mltable.to_pandas_dataframe().dtypes
        assert new_column_types['PassengerId'].name == 'int64'
        assert new_column_types['Fare'].name == 'float64'
        assert new_column_types['Pclass'].name == 'int64'
        assert new_column_types['Ticket'].name == 'object'
        assert new_column_types['Survived'].name == 'bool'

    def test_convert_string_sdk(self, get_mltable_with_type):
        # in pandas all values string by default, so need extra logic to check string conversion works
        pre_mltable = get_mltable_with_type.convert_column_types({'Sex': DataType.to_int()})
        pre_column_types = pre_mltable.to_pandas_dataframe().dtypes
        assert pre_column_types['Sex'].name == 'int64'

        post_mltable = get_mltable_with_type.convert_column_types({'Sex': DataType.to_string()})
        post_column_types = post_mltable.to_pandas_dataframe().dtypes
        # string is object type
        assert post_column_types['Sex'].name == 'object'

    def test_convert_datetime_sdk(self, get_trait_timestamp_mltable):
        self.assert_all_cols_are_object(get_trait_timestamp_mltable)
        data_types = {
            'datetime': DataType.to_datetime('%Y-%m-%d %H:%M:%S'),
            'date': DataType.to_datetime('%Y-%m-%d'),
            'only_timevalues': DataType.to_datetime('%Y-%m-%d %H:%M:%S', '2020-01-01 ')
        }
        new_column_types = get_trait_timestamp_mltable.convert_column_types(data_types).to_pandas_dataframe().dtypes
        assert new_column_types['datetime'].name == 'datetime64[ns]'
        assert new_column_types['date'].name == 'datetime64[ns]'
        assert new_column_types['only_timevalues'].name == 'datetime64[ns]'

    def test_convert_multiple_columns(self, get_trait_timestamp_mltable):
        self.assert_all_cols_are_object(get_trait_timestamp_mltable)

        data_types = {('datetime', 'date'): DataType.to_datetime(['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']),
                      ('latitude', 'windSpeed'): DataType.to_float(),
                      ('wban', 'usaf'): DataType.to_int(),
                      'precipTime': DataType.to_float()}

        converted_col_types = get_trait_timestamp_mltable.convert_column_types(data_types).to_pandas_dataframe().dtypes
        assert converted_col_types['datetime'].name == 'datetime64[ns]'
        assert converted_col_types['date'].name == 'datetime64[ns]'
        assert converted_col_types['latitude'].name == 'float64'
        assert converted_col_types['windSpeed'].name == 'float64'
        assert converted_col_types['precipTime'].name == 'float64'
        assert converted_col_types['wban'].name == 'int64'
        assert converted_col_types['usaf'].name == 'int64'

    def test_convert_boolean_sdk(self, get_mltable_with_type):
        # data types are not automatically inferred for sake of this test
        old_column_types = get_mltable_with_type.to_pandas_dataframe().dtypes
        assert old_column_types['Sex'].name == 'object'

        mltable_without_inputs = get_mltable_with_type.convert_column_types({'Sex': DataType.to_bool()})
        mltable_with_full_inputs = get_mltable_with_type.convert_column_types(
            {'Sex': DataType.to_bool(true_values=['1'], false_values=['0'], mismatch_as='error')})

        mltable_without_inputs_types = mltable_without_inputs.to_pandas_dataframe().dtypes
        mltable_with_full_inputs_types = mltable_with_full_inputs.to_pandas_dataframe().dtypes

        assert mltable_without_inputs_types['Sex'].name == 'bool'
        assert mltable_with_full_inputs_types['Sex'].name == 'bool'

    def test_convert_empty_conversion(self, get_trait_timestamp_mltable):
        exp_err_msg = 'Expected a non-empty dict\\[Union\\[str, tuple\\[str\\]\\], Union\\[str, mltable.DataType\\]\\]'
        with pytest.raises(UserErrorException, match=exp_err_msg):
            get_trait_timestamp_mltable.convert_column_types({})

    def test_convert_dup_cols(self, get_trait_timestamp_mltable):
        exp_err_msg = "Found duplicate column. Cannot convert column 'latitude' to multiple `mltable.DataType`s."
        with pytest.raises(UserErrorException, match=exp_err_msg):
            get_trait_timestamp_mltable.convert_column_types({('latitude', 'windSpeed'): DataType.to_float(),
                                                              ('wban', 'latitude'): DataType.to_int()})

    def test_convert_yaml(self, get_data_folder_path):
        mltable = load(os.path.join(get_data_folder_path, 'mltable_convert_column_types/simple_types_yaml'))
        column_types = mltable.to_pandas_dataframe().dtypes
        assert column_types['datetime'].name == 'datetime64[ns]'
        assert column_types['date'].name == 'datetime64[ns]'
        assert column_types['latitude'].name == 'float64'
        assert column_types['stationName'].name == 'object'
        assert column_types['wban'].name == 'int64'
        assert column_types['gender'].name == 'bool'
        assert column_types['only_timevalues'].name == 'datetime64[ns]'

    def test_convert_multiple_cols_yaml(self, get_data_folder_path):
        mltable = load(os.path.join(get_data_folder_path, 'mltable_convert_column_types/simple_types_multiple_cols'))
        column_types = mltable.to_pandas_dataframe().dtypes
        assert column_types['datetime'].name == 'datetime64[ns]'
        assert column_types['date'].name == 'datetime64[ns]'
        assert column_types['latitude'].name == 'float64'
        assert column_types['windSpeed'].name == 'float64'
        assert column_types['wban'].name == 'int64'
        assert column_types['usaf'].name == 'int64'

    def test_stream_info_no_workspace_sdk(self, get_data_folder_path):
        mltable = load(os.path.join(get_data_folder_path, 'mltable_convert_column_types/stream_info_uri_formats'))
        data_types = {
            'image_url': DataType.to_stream(),
            'long_form_uri': DataType.to_stream(),
            'direct_uri_wasbs': DataType.to_stream(),
            'direct_uri_abfss': DataType.to_stream(),
            'direct_uri_adl': DataType.to_stream()
        }
        new_mltable = mltable.convert_column_types(data_types)
        df = new_mltable.to_pandas_dataframe()
        stream_info_class_name = StreamInfo.__name__
        none_uri = type(df['image_url'][0]).__name__
        long_form_uri = type(df['long_form_uri'][0]).__name__
        direct_uri_wasbs = type(df['direct_uri_wasbs'][0]).__name__
        direct_uri_abfss = type(df['direct_uri_abfss'][0]).__name__
        direct_uri_adl = type(df['direct_uri_adl'][0]).__name__
        assert none_uri == 'NoneType'  # None since this url has no workspace info in it
        assert long_form_uri == stream_info_class_name
        assert direct_uri_wasbs == stream_info_class_name
        assert direct_uri_abfss == stream_info_class_name
        assert direct_uri_adl == stream_info_class_name

    def test_convert_stream_info_yaml(self, get_data_folder_path):
        string_path = 'mltable_convert_column_types/stream_info_yaml'
        path = os.path.join(get_data_folder_path, string_path)
        mltable = load(path)
        df = mltable.to_pandas_dataframe()
        stream_info_class_name = StreamInfo.__name__
        long_form_uri = type(df['long_form_uri'][0]).__name__
        direct_uri_wasbs = type(df['direct_uri_wasbs'][0]).__name__
        direct_uri_abfss = type(df['direct_uri_abfss'][0]).__name__
        direct_uri_adl = type(df['direct_uri_adl'][0]).__name__
        assert long_form_uri == stream_info_class_name
        assert direct_uri_wasbs == stream_info_class_name
        assert direct_uri_abfss == stream_info_class_name
        assert direct_uri_adl == stream_info_class_name

    def test_empty_columns_sdk(self, get_mltable):
        with pytest.raises(UserErrorException,
                           match='Expect column names to be single strings or non-empty tuples of strings.'):
            get_mltable.convert_column_types({tuple(): 'string'})

    def test_empty_columns_yaml(self):
        # TODO
        pass
