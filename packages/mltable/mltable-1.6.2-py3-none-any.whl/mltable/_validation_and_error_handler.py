# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.dataprep import UserErrorException
from azureml.dataprep.api.mltable._validation_and_error_handler import _RSLEX_USER_ERROR_VALUES


def _validate_downloads(download_records, ignore_not_found, logger):
    if not download_records:
        return []

    try_clex = True
    try:
        from azureml.dataprep.rslex import StreamInfo as RSlexStreamInfo, PyErrorValue
        try_rslex = True
    except ImportError:  # TODO (nathof) remove clex fallback after rslex release
        try_rslex = False

    from azureml.dataprep.native import StreamInfo as NativeStreamInfo, DataPrepError

    downloaded_files = []
    errors = []

    def parse_rslex_value(value):
        if isinstance(value, RSlexStreamInfo):
            downloaded_files.append(value.resource_id)
            return True
        if isinstance(value, PyErrorValue):
            error_code = value.error_code
            source_value = value.source_value
            if ignore_not_found and error_code == 'Microsoft.DPrep.ErrorValues.SourceFileNotFound':
                logger.warning(f"'{source_value}' hasn't been downloaded as it was not present at the source. \
                                Download is proceeding.")
            else:
                errors.append((source_value, error_code))
            return True
        return False

    def parse_clex_value(value):
        if isinstance(value, NativeStreamInfo):
            downloaded_files.append(value.resource_identifier)
            return True
        if isinstance(value, DataPrepError):
            resource_identifier = value.originalValue
            error_code = value.errorCode
            if ignore_not_found and error_code == 'Microsoft.DPrep.ErrorValues.SourceFileNotFound':
                logger.warning(f"'{resource_identifier}' hasn't been downloaded as it was not present at the source. \
                                Download is proceeding.")
            else:
                errors.append((resource_identifier, error_code))
            return True
        return False

    for record in download_records:
        # would like to deduplicate near identical code but values have different attribute names
        if isinstance(record, dict):  # either from rslex or clex
            value = record['DestinationFile']
        else:
            try:  # TODO (nathof) remove PyRecord & Clex handing after dprep release, PyRecord is no longer returned
                from azureml.dataprep.rslex import PyRecord
                if isinstance(record, PyRecord):  # definitely from clex
                    value = record.get_value('DestinationFile')
                    try_clex = False
                else:
                    raise RuntimeError(
                        f'Received value has unexpected type during file download: {record}')
            except ImportError:
                raise RuntimeError(
                    f'Received value has unexpected type during file download: {record}')

        if not ((try_rslex and parse_rslex_value(value)) or (try_clex and parse_clex_value(value))):
            raise RuntimeError(f'Unexpected error during file download: {value}')

    if errors:
        _download_error_handler(errors)
    return downloaded_files


def _download_error_handler(errors):
    non_user_errors = list(filter(lambda x: x[1] not in _RSLEX_USER_ERROR_VALUES, errors))
    if non_user_errors:
        raise RuntimeError(f'System errors occured during downloading: {non_user_errors}')
    errors = '\n'.join(map(str, errors))
    raise UserErrorException(f'Some files have failed to download: {errors}')
