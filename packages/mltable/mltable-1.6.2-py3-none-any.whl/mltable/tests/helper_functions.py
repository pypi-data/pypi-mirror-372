import copy
import os.path

import tempfile
import yaml

from mltable.mltable import load, _read_yaml


def mltable_was_loaded(mltable):
    df = mltable.to_pandas_dataframe()
    assert df is not None
    assert not df.empty
    return df


def can_load_mltable(uri, storage_options=None):
    try:
        mltable = load(uri=uri, storage_options=storage_options)
    except Exception as e:
        assert False, f'failed to load MLTable, got error [{type(e)}: {e}]'

    _test_save_load_round_trip(mltable, storage_options)
    return mltable_was_loaded(mltable)


def _test_save_load_round_trip(mltable, storage_options=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        mltable.save(temp_dir, colocated=True)
        loaded_mltable = load(temp_dir, storage_options=storage_options)
        # MLTables are same after roundtrip
        assert mltable == loaded_mltable

        # same data can be fetched
        original_df = mltable.to_pandas_dataframe()
        assert original_df is not None

        loaded_df = loaded_mltable.to_pandas_dataframe()
        assert loaded_df is not None

        assert original_df.equals(loaded_df)


def mltable_as_dict(mltable):
    """
    Given a MLTable, returns it's underlying Dataflow (added transformation steps, metadata, etc.)
    as a dictionary
    """
    return yaml.safe_load(mltable._dataflow.to_yaml_string())


def get_mltable_and_dicts(path):
    mltable = load(path)
    return mltable, mltable_as_dict(mltable), _read_yaml(path)


def get_invalid_mltable(get_invalid_data_folder_path):
    return load(get_invalid_data_folder_path)


def save_mltable_yaml_dict(save_dirc, mltable_yaml_dict):
    save_path = os.path.join(save_dirc, 'MLTable')
    with open(save_path, 'w') as f:
        yaml.safe_dump(mltable_yaml_dict, f)
    return save_path


def list_of_dicts_equal(a, b, c=None):
    b = copy.deepcopy(b)
    assert len(a) == len(b)
    for x in a:
        b.remove(x)
    assert len(b) == 0

    if c is not None:
        list_of_dicts_equal(a, c)
