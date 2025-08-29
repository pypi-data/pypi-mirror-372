"""Au Packet"""

import sys

from deprecated import deprecated

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ServerPacket


@deprecated(version='3.0', reason='This packet is deprecated and will be removed in v4.0')
class AuPacket(ServerPacket):
  """Au packet definition"""

  @staticmethod
  def from_packet(raw: str) -> 'AuPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Au>') or not raw.endswith('</Au>'):
      raise MalformedException('Invalid packet definition, should be <Au>...</Au>')

    parts = raw[4:-5].split(';')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    return AuPacket()

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = ';'
    crc = str(hex(calculate_crc(raw.encode())))[2:].upper().zfill(4)

    return f'<Au>{raw}{crc}</Au>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
