"""Parser functions for the layrz_protocol module."""

import re
from typing import Any

from layrz_protocol.constants import ASCII_MAP


def parse_extra(raw: str) -> dict[str, Any]:
  """
  Parse extra args following this structure
  `key1:value1,key2:value2,key3:value3`
  """
  if len(raw) == 0:
    return {}

  result = {}
  for param in raw.split(','):
    value: Any
    key, value = param.split(':', maxsplit=1)

    if re.match(r'^io[0-9]+\.di$', key):  # Digital input
      gpio = key.replace('io', '').replace('.di', '')
      key = f'gpio.{gpio}.digital.input'

    elif re.match(r'^io[0-9]+\.do$', key):  # Digital output
      gpio = key.replace('io', '').replace('.do', '')
      key = f'gpio.{gpio}.digital.output'

    elif re.match(r'^io[0-9]+\.ai$', key):  # Analog input
      gpio = key.replace('io', '').replace('.ai', '')
      key = f'gpio.{gpio}.analog.input'

    elif re.match(r'^io[0-9]+\.ao$', key):  # Analog output
      gpio = key.replace('io', '').replace('.ao', '')
      key = f'gpio.{gpio}.analog.output'

    elif re.match(r'^io[0-9]+\.counter$', key):  # Counter
      gpio = key.replace('io', '').replace('.counter', '')
      key = f'gpio.{gpio}.event.count'

    elif re.match(r'^ble.[0-9]+\.id$', key):  # BLE ID
      ble = key.replace('ble.', '').replace('.id', '')
      key = f'ble.{ble}.mac.address'

    elif re.match(r'^ble.[0-9]+\.hum$', key):  # BLE Humidity value
      ble = key.replace('ble.', '').replace('.hum', '')
      key = f'ble.{ble}.humidity'

    elif re.match(r'^ble.[0-9]+\.tempc$', key):  # BLE Temperature value in Celsius
      ble = key.replace('ble.', '').replace('.tempc', '')
      key = f'ble.{ble}.temperature.celsius'

    elif re.match(r'^ble.[0-9]+\.tempf$', key):  # BLE Temperature value in Fahrenheit
      ble = key.replace('ble.', '').replace('.tempf', '')
      key = f'ble.{ble}.temperature.fahrenheit'

    elif re.match(r'^ble.[0-9]+\.model_id$', key):  # BLE Model ID
      ble = key.replace('ble.', '').replace('.model_id', '')
      key = f'ble.{ble}.model.id'

    elif re.match(r'^ble.[0-9]+\.batt$', key):  # BLE Battery level
      ble = key.replace('ble.', '').replace('.batt', '')
      key = f'ble.{ble}.battery.level'

    elif re.match(r'^ble.[0-9]+\.lux$', key):  # BLE Light level
      ble = key.replace('ble.', '').replace('.lux', '')
      key = f'ble.{ble}.light.level.lux'

    elif re.match(r'^ble.[0-9]+\.volt$', key):  # BLE Voltage level
      ble = key.replace('ble.', '').replace('.volt', '')
      key = f'ble.{ble}.voltage'

    elif re.match(r'^ble.[0-9]+\.rpm$', key):  # BLE RPM value
      ble = key.replace('ble.', '').replace('.rpm', '')
      key = f'ble.{ble}.rpm'

    elif re.match(r'^ble.[0-9]+\.press$', key):  # BLE Pressure value
      ble = key.replace('ble.', '').replace('.press', '')
      key = f'ble.{ble}.pressure'

    elif re.match(r'^ble.[0-9]+\.counter$', key):  # BLE event counter
      ble = key.replace('ble.', '').replace('.counter', '')
      key = f'ble.{ble}.event.count'

    elif re.match(r'^ble.[0-9]+\.x_acc$', key):  # BLE X-axis acceleration
      ble = key.replace('ble.', '').replace('.x_acc', '')
      key = f'ble.{ble}.acceleration.x'

    elif re.match(r'^ble.[0-9]+\.y_acc$', key):  # BLE Y-axis acceleration
      ble = key.replace('ble.', '').replace('.y_acc', '')
      key = f'ble.{ble}.acceleration.y'

    elif re.match(r'^ble.[0-9]+\.z_acc$', key):  # BLE Z-axis acceleration
      ble = key.replace('ble.', '').replace('.z_acc', '')
      key = f'ble.{ble}.acceleration.z'

    elif re.match(r'^ble.[0-9]+\.msg_count$', key):  # BLE message count
      ble = key.replace('ble.', '').replace('.msg_count', '')
      key = f'ble.{ble}.message.count'

    elif re.match(r'^ble.[0-9]+\.msg$', key):  # BLE message
      ble = key.replace('ble.', '').replace('.msg', '')
      key = f'ble.{ble}.message'

    elif re.match(r'^ble.[0-9]+\.mag_counter', key):  # BLE magnetic event counter
      ble = key.replace('ble.', '').replace('.mag_counter', '')
      key = f'ble.{ble}.magnetic.event.count'

    elif re.match(r'^ble.[0-9]+\.mag_data', key):  # BLE magnetic data
      ble = key.replace('ble.', '').replace('.mag_data', '')
      key = f'ble.{ble}.magnetic.data'

    elif re.match(r'^ble.[0-9]+\.rssi', key):  # BLE RSSI
      ble = key.replace('ble.', '').replace('.rssi', '')
      key = f'ble.{ble}.rssi.dbm'

    elif key == 'report':  # Report code
      key = 'report.code'

    elif key == 'confiot_ble':  # ConfIoT BLE connection status
      key = 'ble.confiot.connection.status'

    elif key == 'confiot_serial':  # ConfIoT Serial connection status
      key = 'serial.confiot.connection.status'

    if re.match(r'^-?[0-9]{1,}+(\.[0-9]{1,})$', value):
      value = float(value)
    elif re.match(r'^-?[0-9]{1,}+$', value):
      value = int(value)
    elif value.lower() in ['true', 'false', 't', 'f']:
      value = value.lower() == 'true'
    else:
      value = value

    result[key] = value

  return result


def cast_extra(extra: dict[str, Any]) -> str:
  """
  Cast extra args to string following this structure
  `key1:value1,key2:value2,key3:value3`
  """
  payload = {}

  for key, value in extra.items():
    payload.update(convert_to_dotcase(key, value))

  extra_list: list[str] = []
  for key, value in payload.items():
    if isinstance(value, bool):
      extra_list.append(f'{key}:{"true" if value else "false"}')
    else:
      extra_list.append(f'{key}:{value}')

  return ','.join(extra_list)


def convert_to_dotcase(key: str, value: Any) -> dict[str, Any]:
  """Read parameter"""
  if value is None:
    return {}

  if isinstance(value, list):
    command = {}
    for i, item in enumerate(value):
      command.update(convert_to_dotcase(key=f'{key}.{i}', value=item))
    return command

  if isinstance(value, dict):
    command = {}
    for k, v in value.items():
      command.update(convert_to_dotcase(key=f'{key}.{k}', value=v))
    return command

  if isinstance(value, str):
    for char in value:
      if char in ASCII_MAP:
        value = value.replace(char, ASCII_MAP[char])

    return {key: value}

  return {key: value}
