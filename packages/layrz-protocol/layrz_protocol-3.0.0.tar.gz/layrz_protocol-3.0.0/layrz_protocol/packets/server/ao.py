"""Ao Packet"""

import sys
from datetime import datetime
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ServerPacket


class AoPacket(ServerPacket):
  """Ao packet definition"""

  timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), description='Timestamp of the packet')

  @staticmethod
  def from_packet(raw: str) -> 'AoPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Ao>') or not raw.endswith('</Ao>'):
      raise MalformedException('Invalid packet definition, should be <Ao>...</Ao>')

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

    try:
      timestamp = datetime.fromtimestamp(int(parts[0]), tz=UTC)
    except ValueError as e:
      raise MalformedException('Invalid timestamp, should be an int') from e

    return AoPacket(timestamp=timestamp)

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Ao>{raw}{crc}</Ao>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()

  @field_validator('timestamp', mode='before')
  def _validate_timestamp(cls, value: Any) -> datetime:
    """Validate timestamp"""
    if value is None:
      return datetime.now(tz=UTC)

    if isinstance(value, (int, float)):
      return datetime.fromtimestamp(value, tz=UTC)

    if isinstance(value, datetime):
      return value

    return datetime.fromtimestamp(value, tz=UTC)
