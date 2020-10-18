"""Unittest of __main__.py."""
from unittest import mock

import pytest

from Arbie.__main__ import main

document = """
  a: 1
  b:
    c: 3
    d: 4
"""


class TestMain(object):

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            main(['-f', 'giberich.yml'])

    def test_open_yaml_file(self):
        # test valid yaml
        mock_open = mock.mock_open(read_data=document)
        with mock.patch('builtins.open', mock_open):
            main(['-f', 'giberich.yml'])
