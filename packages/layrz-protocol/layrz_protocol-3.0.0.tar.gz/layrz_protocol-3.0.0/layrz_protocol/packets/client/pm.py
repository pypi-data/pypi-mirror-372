"""Pm Packet"""

import base64
import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException

from .base import ClientPacket


class PmPacket(ClientPacket):
  """Pm packet definition"""

  filename: str = Field(..., description='Filename of the packet')
  content_type: str = Field(..., description='Content type of the packet')
  data: bytes = Field(..., description='Data of the packet')

  @staticmethod
  def from_packet(raw: str) -> 'PmPacket':
    """Creates a media packet"""
    if not raw.startswith('<Pm>') or not raw.endswith('</Pm>'):
      raise MalformedException('Invalid packet definition, should be <Pm>...</Pm>')
    parts = raw[4:-5].split(';')

    if len(parts) != 4:
      raise MalformedException('Invalid packet definition')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    try:
      data = base64.b64decode(parts[2])
    except ValueError as e:
      raise MalformedException('Invalid base64 data') from e

    return PmPacket(
      filename=parts[0],
      content_type=parts[1],
      data=data,
    )

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    raw = f'{self.filename};{self.content_type};'
    raw += base64.b64encode(self.data).decode() + ';'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pm>{raw}{crc}</Pm>'

  def __str__(self: Self) -> str:
    """Return the string representation of the packet"""
    return self.to_packet()
