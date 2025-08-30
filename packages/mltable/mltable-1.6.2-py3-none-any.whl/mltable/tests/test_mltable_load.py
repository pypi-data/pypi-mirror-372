import os

from azureml.dataprep import UserErrorException
import pytest

from mltable import load
from .helper_functions import can_load_mltable, get_invalid_mltable, get_mltable_and_dicts, list_of_dicts_equal, \
    mltable_as_dict, _read_yaml


@pytest.mark.mltable_sdk_unit_test
class TestMLTableLoad:
    def test_load_mltable(self, get_mltable):
        mltable = get_mltable
        assert mltable is not None

    def test_load_invalid_mltable(self, get_invalid_data_folder_path):
        with pytest.raises(UserErrorException, match='Given MLTable does not adhere to the AzureML MLTable schema:.*'):
            get_invalid_mltable(get_invalid_data_folder_path)

    def test_load_mltable_with_mixed_casing(self, get_data_folder_path):
        # loads a dataset from a path with both upper and lower case letters
        data_folder_path = os.path.join(get_data_folder_path, 'MLTable_case')
        can_load_mltable(uri=data_folder_path)

    def test_load_mltable_with_unicode(self, get_data_folder_path):
        # loads tabular mltable from paths with non-ascii unicode characters
        for char in 'Ǣ', 'Ɖ', 'Ƙ', 'Ƹ':
            path = f'mltable_unicode/{char}'
            data_folder_path = os.path.join(get_data_folder_path, path)
            can_load_mltable(uri=data_folder_path)

    def test_load_relative_paths(self, get_mltable, get_mltable_data_folder_path):
        # relative paths are in the saved MLTable file
        rel_paths = [{'file': os.path.normpath('Titanic2.csv')}, {'file': os.path.normpath('subfolder/Titanic2.csv')}]
        mltable_yaml_file_dict = _read_yaml(get_mltable_data_folder_path)
        paths = [{k: os.path.normpath(v) for k, v in d.items()} for d in mltable_yaml_file_dict['paths']]
        list_of_dicts_equal(paths, rel_paths)

        # relative paths are made absolute in MLTable's Dataflow after loading
        mltable = get_mltable
        expected_paths = [
            {'file': 'file://' + os.path.normpath(os.path.join(get_mltable_data_folder_path, 'Titanic2.csv'))},
            {'file':
             'file://' + os.path.normpath(os.path.join(get_mltable_data_folder_path, 'subfolder/Titanic2.csv'))}
        ]
        list_of_dicts_equal(mltable_as_dict(mltable)['paths'], expected_paths)

        # relative paths are preserved in `MLTable.paths`
        paths = [{k: os.path.normpath(v) for k, v in d.items()} for d in mltable.paths]
        list_of_dicts_equal(paths, rel_paths)

    def test_load_relative_mltable(self, get_dir_folder_path):
        cwd = get_dir_folder_path
        os.chdir(cwd)

        # loads mltable from relative path by mimicking to be in a local folder
        relative_path = './data/mltable/mltable_relative'
        mltable = load(relative_path)
        mltable_yaml_dict = _read_yaml(relative_path)
        assert mltable_yaml_dict is not None
        assert mltable._dataflow.to_yaml_string() is not None
        for path_dict in mltable.paths:
            assert os.path.exists(os.path.join(relative_path, path_dict['file']))

    def test_load_mltable_with_arbitrary_metadata(self, get_data_folder_path):
        mltable_dirc = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc, 'mltable_arb_metadata')
        can_load_mltable(mltable_path)

    def test_load_mltable_with_invalid_url(self):
        # TODO redo this _download_yaml exceptions
        with pytest.raises(UserErrorException) as e:
            load('https://raw.githubusercontent.com/microsoft/arcticseals/master/data/test.csv')
            assert e.message == 'The requested stream was not found. Please make sure the request uri is correct.'
            assert e.error_code == 'ScriptExecution.StreamAccess.NotFound'

    def test_mltable_load_with_auth(self, get_data_folder_path):
        auth_dict = {
            'authType': 'ServicePrincipal',
            'service_principal_id': 'b74fa1b7-9468-468a-ab0a-00062eb9e884',
            'service_principal_password': 'xxxx',
            'cloudType': 'AzureCloud',
            'tenantId': '72f988bf-86f1-41af-91ab-2d7cd011db47',
        }
        storage_options = {'auth_dict': auth_dict}
        data_folder_path = os.path.join(get_data_folder_path, 'MLTable_case')
        can_load_mltable(uri=data_folder_path, storage_options=storage_options)

        from azureml.dataprep.api._datastore_helper import _get_auth
        auth_type, auth_value = _get_auth()
        from azureml.dataprep.api.engineapi.typedefinitions import AuthType
        assert auth_type == AuthType.SERVICEPRINCIPAL
        converted_auth_dict = {
            'cloudType': 'AzureCloud',
            'password': 'xxxx',
            'servicePrincipalId': 'b74fa1b7-9468-468a-ab0a-00062eb9e884',
            'tenantId': '72f988bf-86f1-41af-91ab-2d7cd011db47',
        }
        assert auth_value == converted_auth_dict

    def test_mltable_load_with_auth_msi(self, get_data_folder_path):
        auth_dict = {
            'authType': 'Managed',
            'clientId': 'cb7061a4-0533-4703-ad92-9f344169452f',
            'endpointType': 'MsiEndpoint',
            'cloudType': 'AzureCloud',
            'tenantId': '72f988bf-86f1-41af-91ab-2d7cd011db47',
            'authority': 'login.microsoftonline.com',
        }
        storage_options = {'auth_dict': auth_dict}
        data_folder_path = os.path.join(get_data_folder_path, 'MLTable_case')
        can_load_mltable(uri=data_folder_path, storage_options=storage_options)

        from azureml.dataprep.api._datastore_helper import _get_auth
        auth_type, auth_value = _get_auth()
        from azureml.dataprep.api.engineapi.typedefinitions import AuthType
        assert auth_type == AuthType.MANAGED
        converted_auth_dict = {
            'authority': 'login.microsoftonline.com',
            'clientId': 'cb7061a4-0533-4703-ad92-9f344169452f',
            'cloudType': 'AzureCloud',
            'endpointType': 'MsiEndpoint',
            'tenantId': '72f988bf-86f1-41af-91ab-2d7cd011db47'
        }
        assert auth_value == converted_auth_dict

    def test_load_mltable_pattern_invalid_file_path(self, get_data_folder_path):
        data_folder_path = os.path.join(get_data_folder_path, 'mltable_pattern')
        with pytest.raises(UserErrorException) as e:
            can_load_mltable(uri=data_folder_path)
            assert e.error_code == 'ScriptExecution.Validation'


@pytest.mark.mltable_sdk_unit_test_windows
class TestMLTableLoadWindowsOnly:
    def test_load(self, get_data_folder_path):
        mltable_dirc_path = get_data_folder_path
        mltable_path = os.path.join(mltable_dirc_path, 'mltable_windows')
        og_mltable, og_mltable_yaml_dict, og_mltable_yaml_file_dict = get_mltable_and_dicts(mltable_path)

        # paths before loading are preserved in paths attribute
        list_of_dicts_equal([{'file': 'D:\\absolute\\path\\file.csv'}, {'file': 'relative\\path\\file.csv'}],
                            og_mltable_yaml_file_dict['paths'],
                            og_mltable.paths)

        # paths in MLTable Dataflow after loading
        list_of_dicts_equal([{'file': 'file://D:\\absolute\\path\\file.csv'},
                             {'file': 'file://' + os.path.join(mltable_path, 'relative\\path\\file.csv')}],
                            og_mltable_yaml_dict['paths'])
