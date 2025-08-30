import pytest
from azureml.dataprep.native import DataPrepError, StreamInfo
from azureml.dataprep import UserErrorException

from mltable._validation_and_error_handler import _download_error_handler, _validate_downloads
from mltable.mltable import _get_logger


@pytest.mark.mltable_sdk_unit_test
class TestValidationErrorHandler:

    def test_download_error_handler(self):
        value_error_list = [('dummyFile1.csv', "Microsoft.DPrep.ErrorValues.SourceFileNotFound"),
                            ('dummyFile2.csv', "Microsoft.DPrep.ErrorValues.SourceFilePermissionDenied"),
                            ('dummyFile3.csv', "Microsoft.DPrep.ErrorValues.InvalidArgument"),
                            ('dummyFile4.csv', "Microsoft.DPrep.ErrorValues.SourcePermissionDenied"),
                            ('dummyFile5.csv', "Microsoft.DPrep.ErrorValues.DestinationPermissionDenied"),
                            ('dummyFile6.csv', "Microsoft.DPrep.ErrorValues.DestinationDiskFull"),
                            ('dummyFile7.csv', "Microsoft.DPrep.ErrorValues.FileSizeChangedWhileDownloading"),
                            ('dummyFile8.csv', "Microsoft.DPrep.ErrorValues.StreamInfoInvalidPath"),
                            ('dummyFile9.csv', "Microsoft.DPrep.ErrorValues.NoManagedIdentity"),
                            ('dummyFile10.csv', "Microsoft.DPrep.ErrorValues.NoOboEndpoint"),
                            ('dummyFile11.csv', "Microsoft.DPrep.ErrorValues.StreamInfoRequired")]

        with pytest.raises(UserErrorException, match='Some files have failed to download: .*'):
            _download_error_handler(value_error_list)

        with pytest.raises(RuntimeError, match='System errors occured during downloading: .*'):
            _download_error_handler([('dummyFile.csv', 'Microsoft.DPrep.ErrorValues.IntegerOverflow')])

    def test_validate_downloads(self):
        # Empty download_records
        assert _validate_downloads([], False, _get_logger()) == []

        # Does not raise exception since the error is related to no file found in source thus returns empty list
        download_records = [{'DestinationFile': DataPrepError("Microsoft.DPrep.ErrorValues.SourceFileNotFound",
                                                              originalValue="Path",
                                                              properties="")}]
        assert _validate_downloads(download_records, True, _get_logger()) == []

        # Error found in download_records
        download_records = [{'DestinationFile': DataPrepError("Microsoft.DPrep.ErrorValues.InvalidArgument",
                                                              originalValue="Path",
                                                              properties="")}]
        with pytest.raises(UserErrorException, match='Some files have failed to download:.*'):
            _validate_downloads(download_records, False, _get_logger())

        # Raises RuntimeError
        with pytest.raises(RuntimeError, match="Unexpected error during file download.*"):
            _validate_downloads([{'DestinationFile': 'expectingRuntimeError'}], False, _get_logger())

        # Happy path
        stream_info_object = StreamInfo(handler='Local', arguments={}, resource_identifier='C:/path/Titanic2.csv')
        download_records = [{'DestinationFile': stream_info_object}]
        assert _validate_downloads(download_records, False, _get_logger()) == ['C:/path/Titanic2.csv']
