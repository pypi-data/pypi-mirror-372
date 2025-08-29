"""Test Server Packets"""

import pytest

from layrz_protocol.packets import AbPacket, AcPacket, AoPacket, ArPacket, Command
from layrz_protocol.utils import calculate_crc


def test2_ao_packet() -> None:
  payload = '1;'  # message_id
  crc = str(hex(calculate_crc(f'{payload}'.encode())))[2:].upper().zfill(4)

  payload = f'<Ao>{payload}{crc}</Ao>'
  msg: AoPacket = AoPacket.from_packet(payload)

  assert msg.to_packet() == payload


def test2_ar_packet() -> None:
  payload = 'CRC mismatch;'  # message_id
  crc = str(hex(calculate_crc(f'{payload}'.encode())))[2:].upper().zfill(4)

  payload = f'<Ar>{payload}{crc}</Ar>'
  msg: ArPacket = ArPacket.from_packet(payload)

  assert msg.reason == 'CRC mismatch'
  assert msg.to_packet() == payload


def test2_ac_packet() -> None:
  cmd1 = Command(
    command_id=1,
    command_name='get_msg',
    args={},
  )
  cmd2 = Command(
    command_id=2,
    command_name='set_config',
    args={
      'wifi_ssid': 'test',
    },
  )

  payload1 = f'{cmd1.command_id};{cmd1.command_name};;'
  crc = str(hex(calculate_crc(payload1.encode())))[2:].upper().zfill(4)
  payload1 += f'{crc}'

  assert cmd1.to_packet() == payload1

  payload2 = f'{cmd2.command_id};{cmd2.command_name};wifi_ssid:test;'
  crc = str(hex(calculate_crc(payload2.encode())))[2:].upper().zfill(4)
  payload2 += f'{crc}'

  assert cmd2.to_packet() == payload2

  payload = f'{payload1};{payload2};'
  crc = str(hex(calculate_crc(payload.encode())))[2:].upper().zfill(4)

  payload = f'<Ac>{payload}{crc}</Ac>'
  msg: AcPacket = AcPacket.from_packet(payload)

  assert msg.to_packet() == payload

  assert len(msg.commands) == 2
  assert msg.commands[0].command_id == cmd1.command_id
  assert msg.commands[0].command_name == cmd1.command_name
  assert msg.commands[0].args == cmd1.args

  assert msg.commands[1].command_id == cmd2.command_id
  assert msg.commands[1].command_name == cmd2.command_name
  assert msg.commands[1].args == cmd2.args


def test2_ab_packet() -> None:
  payload = '<Ab>1234567890AB:GENERIC;BC0987654321:GENERIC;C1BE</Ab>'
  msg: AbPacket = AbPacket.from_packet(payload)

  assert len(msg.devices) == 2

  assert msg.devices[0].mac_address, '12:34:56:78:90:AB'
  assert msg.devices[0].model, 'GENERIC'

  assert msg.devices[1].mac_address, 'BC:09:87:65:43:21'
  assert msg.devices[1].model, 'GENERIC'

  assert msg.to_packet() == payload
