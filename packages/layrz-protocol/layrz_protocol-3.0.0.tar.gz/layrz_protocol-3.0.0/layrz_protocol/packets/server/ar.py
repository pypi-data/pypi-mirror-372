"""Ar Packet"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ServerPacket


class ArPacket(ServerPacket):
  """Ar packet definition"""

  reason: str = Field(default='Unknown reason', description='Reason for the packet')

  @staticmethod
  def from_packet(raw: str) -> 'ArPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Ar>') or not raw.endswith('</Ar>'):
      raise MalformedException('Invalid packet definition, should be <Ar>...</Ar>')

    parts = raw[4:-5].split(';')
    if len(parts) != 2:
      raise MalformedException('Invalid packet definition, should have 2 parts')

    received_crc: int
    try:
      received_crc = int(parts[1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{parts[0]};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    return ArPacket(reason=parts[0])

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{self.reason};'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Ar>{raw}{crc}</Ar>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
