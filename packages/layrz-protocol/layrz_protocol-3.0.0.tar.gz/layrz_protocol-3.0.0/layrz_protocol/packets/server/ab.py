"""Ab Packet"""

import sys

from layrz_protocol.packets.definitions.ble_data import BleData
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ServerPacket

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field


class AbPacket(ServerPacket):
  """Ab packet definition"""

  devices: list[BleData] = Field(default_factory=list, description='List of BLE devices')

  @staticmethod
  def from_packet(raw: str) -> 'AbPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Ab>') or not raw.endswith('</Ab>'):
      raise MalformedException('Invalid packet definition, should be <Ab>...</Ab>')

    parts = raw[4:-5].split(';')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    parts = parts[:-1]
    if len(parts) % 2 != 0:
      raise MalformedException('Invalid packet definition, should have 4 parts at least')

    try:
      devices = BleData.from_packets(';'.join(parts))
    except Exception as e:
      raise MalformedException('Invalid ble data definition') from e

    return AbPacket(devices=devices)

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = ';'.join([device.to_packet() for device in self.devices]) + ';'
    crc = str(hex(calculate_crc(raw.encode())))[2:].upper().zfill(4)

    return f'<Ab>{raw}{crc}</Ab>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
