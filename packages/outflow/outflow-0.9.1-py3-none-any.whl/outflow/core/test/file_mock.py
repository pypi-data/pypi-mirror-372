# -*- coding: utf-8 -*-
import builtins
from io import BufferedIOBase
from unittest.mock import MagicMock, patch

# Reference to the original open function.
__g__default_open = open


def create_file_mock(*, read_data=None, write_callback=None):
    file_handle = MagicMock(spec=BufferedIOBase)
    file_handle.write = write_callback
    file_handle.__enter__.return_value = file_handle
    file_handle.read.return_value = read_data
    return file_handle


def flexible_mock_open(mocked_files):
    def flexible_side_effect(file_name, *args, **kwargs):
        if file_name in mocked_files:
            return mocked_files[file_name]
        else:
            global __g__default_open  # noqa
            return __g__default_open(file_name, *args, **kwargs)

    return_value = MagicMock(name="open", spec=__g__default_open)
    return_value.side_effect = flexible_side_effect
    return return_value


def patch_open(mocked_files={}):
    return patch.object(builtins, "open", flexible_mock_open(mocked_files))
