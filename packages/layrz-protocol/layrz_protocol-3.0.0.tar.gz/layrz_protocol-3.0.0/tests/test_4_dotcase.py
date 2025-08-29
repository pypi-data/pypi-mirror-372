"""Test Client Packets"""

from typing import Any, List, cast

import pytest

from layrz_protocol.utils import convert_to_dotcase


def test4_dotcase_casting() -> None:
  data = {
    'dict': {
      'key1': 'value1',
      'key2': 'value2',
      'key3': 'value3',
    },
    'list': [
      'value1',
      'value2',
      'value3',
    ],
    'string': 'value',
    'int': 1,
    'float': 1.1,
    'bool': True,
  }

  new_data = {}
  for key, value in data.items():
    new_data.update(convert_to_dotcase(key, value))

  assert new_data['string'] == data['string']
  assert new_data['int'] == data['int']
  assert new_data['float'] == data['float']

  data_dict = cast(dict[str, Any], data['dict'])
  assert new_data['dict.key1'] == data_dict['key1']
  assert new_data['dict.key2'] == data_dict['key2']
  assert new_data['dict.key3'] == data_dict['key3']

  data_list = cast(List[Any], data['list'])
  assert new_data['list.0'] == data_list[0]
  assert new_data['list.1'] == data_list[1]
  assert new_data['list.2'] == data_list[2]
