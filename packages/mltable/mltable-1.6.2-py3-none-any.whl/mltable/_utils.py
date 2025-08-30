# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import re
import yaml

import jsonschema
import jsonschema.exceptions
from azureml.dataprep.api.mltable._mltable_helper import _parse_path_format, _PathType
from azureml.dataprep.api._loggerfactory import _LoggerFactory
from azureml.dataprep import UserErrorException


_logger = _LoggerFactory.get_logger('MLTableUtils')
_long_form_aml_uri = re.compile(
    r'^azureml://subscriptions/([^\/]+)/resourcegroups/([^\/]+)/'
    r'(?:providers/Microsoft.MachineLearningServices/)?workspaces/([^\/]+)/(.*)',
    re.IGNORECASE)


_PATHS_KEY = 'paths'
_FILE_HANDLER = 'file://'


def _is_local_path(path):
    return _parse_path_format(path)[0] == _PathType.local


def _is_remote_path(path):
    return not _is_local_path(path)


def _prepend_file_handler(path):
    return _FILE_HANDLER + path


def _starts_with_file_handler(path):
    return path.startswith(_FILE_HANDLER)


def _remove_file_handler(path):
    return path[len(_FILE_HANDLER):]


def _make_all_paths_absolute(mltable_yaml_dict, base_path):
    def format_path_pair(path_prop, path, is_base_path_local):
        # get absolute path from base_path + relative path
        if _is_local_path(path) and not _starts_with_file_handler(path):
            # assumes that local relative paths are co-located in directory of MLTable file
            path = os.path.normpath(path)

            if not os.path.isabs(path):
                # when path == '.' it represents the current dir, which is base_path ex) folder: .
                path = base_path if _path_is_current_directory_variant(path) else os.path.join(base_path, path)

            if is_base_path_local:
                path = os.path.normpath(path)
                path = _prepend_file_handler(os.path.abspath(path))

        return path_prop, path

    def format_paths(paths, is_base_path_local):
        return list(map(lambda path_dict:
                        tuple([path_dict,
                               dict(map(lambda x:
                                        format_path_pair(*x, is_base_path_local), path_dict.items()))]), paths))

    if base_path and _PATHS_KEY in mltable_yaml_dict:
        path_pairs = format_paths(mltable_yaml_dict[_PATHS_KEY], _is_local_path(base_path))
        mltable_yaml_dict[_PATHS_KEY] = list(map(lambda x: x[1], path_pairs))
    else:
        path_pairs = list(tuple(zip(mltable_yaml_dict[_PATHS_KEY], mltable_yaml_dict[_PATHS_KEY])))
    return mltable_yaml_dict, path_pairs


def _path_is_current_directory_variant(path):
    return path in ['.', './', '.\\']


def _validate(mltable_yaml_dict):
    parent_dirc = os.path.dirname(os.path.abspath(__file__)).rstrip("/")
    mltable_schema_path = f'{parent_dirc}/schema/MLTable.json'
    with open(mltable_schema_path, "r") as stream:
        try:
            schema = json.load(stream)
            jsonschema.validate(mltable_yaml_dict, schema)
        except (json.decoder.JSONDecodeError, jsonschema.exceptions.SchemaError):
            raise UserErrorException("MLTable json schema is not a valid json file.")
        except jsonschema.exceptions.ValidationError as e:
            _logger.warning(f"MLTable validation failed with error: {e.args[0]}")
            raise UserErrorException(f"Given MLTable does not adhere to the AzureML MLTable schema: {e.args[0]}")


# will switch to the api from dataprep package once new dataprep version is released
def _parse_workspace_context_from_longform_uri(uri):
    long_form_uri_match = _long_form_aml_uri.match(uri)

    if long_form_uri_match:
        return {
            'subscription': long_form_uri_match.group(1),
            'resource_group': long_form_uri_match.group(2),
            'workspace_name': long_form_uri_match.group(3)
        }

    return None


def _parse_workspace_context_from_ml_client(mlclient):
    return {
        'subscription': mlclient.subscription_id,
        'resource_group': mlclient.resource_group_name,
        'workspace_name': mlclient.workspace_name
    }


# utility function to remove all the empty and null fields from a nested dict
def _remove_empty_and_null_fields(mltable_yaml_dict):
    if isinstance(mltable_yaml_dict, dict):
        return {k : v for k, v in
                ((k, _remove_empty_and_null_fields(v)) for k, v in mltable_yaml_dict.items()) if v is not None}
    if isinstance(mltable_yaml_dict, list):
        return [v for v in map(_remove_empty_and_null_fields, mltable_yaml_dict) if v is not None]
    return mltable_yaml_dict


class MLTableYamlCleaner(yaml.YAMLObject):
    # _dataflow.to_yaml_string() serializes Serde units (anonymous value containing no data) as nulls.
    # this results in nested fields with empty values being serialized with nulls as values.
    def __init__(self, mltable_yaml_dict):
        self.cleaned_mltable_yaml_dict = _remove_empty_and_null_fields(mltable_yaml_dict)

    def __repr__(self):
        return yaml.dump(self.cleaned_mltable_yaml_dict)


def have_azure_ai_ml() -> bool:
    try:
        import azure.ai.ml  # noqa
        return True
    except ImportError:
        return False


class AzureAiMlImportError(Exception):
    """
    Exception raised when azure-ai-ml was not able to be imported.
    """
    _message = (
        'Could not import the package azure-ai-ml. Ensure a compatible version '
        'is installed by running: pip install azure-ai-ml'
    )

    def __init__(self):
        print('AzureAiMlImportError: ' + self._message)
        super().__init__(self._message)
