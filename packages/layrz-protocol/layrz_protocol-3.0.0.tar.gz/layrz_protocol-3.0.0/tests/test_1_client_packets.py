"""Test Client Packets"""

from datetime import datetime

import pytest

from layrz_protocol.constants import UTC
from layrz_protocol.packets import FirmwareBranch, PcPacket, PdPacket, PiPacket, PsPacket
from layrz_protocol.utils import calculate_crc


def test1_pc_packet() -> None:
  payload = '0;1;Hello world;'
  crc = str(hex(calculate_crc(f'{payload}'.encode())))[2:].upper().zfill(4)

  payload = f'<Pc>{payload}{crc}</Pc>'
  msg: PcPacket = PcPacket.from_packet(payload)

  assert msg.timestamp == datetime.fromtimestamp(0, tz=UTC)
  assert msg.command_id == 1
  assert msg.message == 'Hello world'
  assert msg.to_packet() == payload


def test1_pd_packet() -> None:
  payload = '0;'  # timestamp
  payload += '10.0;'  # LAT
  payload += '10.0;'  # LNG
  payload += '10.0;'  # ALT
  payload += '10.0;'  # SPD
  payload += '10.0;'  # DIR
  payload += '5;'  # SAT
  payload += '1.0;'  # HDOP

  extra = {
    'test.str': 'Hola mundo',
    'test.int': 1,
    'test.double': 1.0,
    'test.bool': True,
  }

  extra_list = []
  for key, value in extra.items():
    if isinstance(value, bool):
      extra_list.append(f'{key}:{"true" if value else "false"}')
    else:
      extra_list.append(f'{key}:{value}')

  payload += f'{",".join(extra_list)};'  # End of extras

  crc = str(hex(calculate_crc(payload.encode())))[2:].upper().zfill(4)
  payload = f'<Pd>{payload}{crc}</Pd>'

  msg: PdPacket = PdPacket.from_packet(payload)

  assert msg.timestamp == datetime.fromtimestamp(0, tz=UTC)
  assert msg.position.latitude == 10.0
  assert msg.position.longitude == 10.0
  assert msg.position.altitude == 10.0
  assert msg.position.speed == 10.0
  assert msg.position.direction == 10.0
  assert msg.position.satellites == 5
  assert msg.position.hdop == 1.0
  assert msg.extra == extra
  assert msg.to_packet() == payload


def test1_pi_packet() -> None:
  ident = 'testident'
  firmware_id = 1
  firmware_build = 1
  device_id = 1
  hardware_id = 1
  model_id = 1
  firmware_branch = FirmwareBranch.DEVELOPMENT
  fota_enabled = True

  payload = f'{ident};'
  payload += f'{firmware_id};'
  payload += f'{firmware_build};'
  payload += f'{device_id};'
  payload += f'{hardware_id};'
  payload += f'{model_id};'
  payload += f'{firmware_branch.value};'
  payload += f'{"1" if fota_enabled else "0"};'

  crc = calculate_crc(payload.encode('utf-8')).to_bytes(2, 'big').hex().upper().zfill(4)

  payload = f'<Pi>{payload}{crc}</Pi>'

  link = PiPacket.from_packet(payload)

  assert link.ident == ident
  assert link.firmware_id == firmware_id
  assert link.firmware_build == firmware_build
  assert link.device_id == device_id
  assert link.hardware_id == hardware_id
  assert link.model_id == model_id
  assert link.firmware_branch == firmware_branch
  assert link.fota_enabled == fota_enabled

  reversed_payload = link.to_packet()
  assert reversed_payload == payload


def test1_ps_packet() -> None:
  payload = '0;'  # timestamp
  extra = {
    'net_wifi_ssid': 'AWESOME WIFI',
    'net_wifi_pass': 'dictadormarico69',  # https://www.youtube.com/watch?v=kq0VUZXiUQs
    'net_wifi_sec': 'WPA2',
    'static.lat': -15.5,
    'static.lng': 15.5,
  }

  extra_list = []
  for key in extra.keys():
    extra_list.append(f'{key}:{extra[key]}')

  payload += f'{",".join(extra_list)};'  # End of extras
  crc = str(hex(calculate_crc(payload.encode('utf-8'))))[2:].upper().zfill(4)

  payload = f'<Ps>{payload}{crc}</Ps>'

  link = PsPacket.from_packet(payload)

  assert link.timestamp == datetime.fromtimestamp(0, tz=UTC)
  assert link.params == extra

  reversed_payload = link.to_packet()
  assert reversed_payload == payload
  assert link.params['net_wifi_ssid'] == extra['net_wifi_ssid']
  assert link.params['net_wifi_pass'] == extra['net_wifi_pass']
  assert link.params['net_wifi_sec'] == extra['net_wifi_sec']
  assert link.params['static.lat'] == extra['static.lat']
  assert link.params['static.lng'] == extra['static.lng']
