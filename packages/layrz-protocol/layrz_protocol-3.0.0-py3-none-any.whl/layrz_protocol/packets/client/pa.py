"""Pa Packet"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException

from .base import ClientPacket


class PaPacket(ClientPacket):
  """Pa packet definition"""

  ident: str = Field(..., description='IMEI or Unique identifier')
  password: str = Field(..., description='Password')

  @staticmethod
  def from_packet(raw: str) -> 'PaPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Pa>') or not raw.endswith('</Pa>'):
      raise MalformedException('Invalid packet definition, should be <Pa>...</Pa>')

    parts = raw[4:-5].split(';')
    if len(parts) != 3:
      raise MalformedException('Invalid packet definition, should have 3 parts')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    return PaPacket(ident=parts[0], password=parts[1])

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{self.ident};{self.password};'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pa>{raw}{crc}</Pa>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
