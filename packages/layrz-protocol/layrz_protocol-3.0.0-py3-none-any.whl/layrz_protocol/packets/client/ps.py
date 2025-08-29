"""Ps Packet"""

import sys
from datetime import datetime
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc, cast_extra, parse_extra

from .base import ClientPacket


class PsPacket(ClientPacket):
  """Ps packet definition"""

  timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), description='Timestamp of the packet')
  params: dict[str, Any] = Field(default_factory=dict, description='Packet parameters')

  @staticmethod
  def from_packet(raw: str) -> 'PsPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Ps>') or not raw.endswith('</Ps>'):
      raise MalformedException('Invalid packet definition, should be <Ps>...</Ps>')

    parts = raw[4:-5].split(';')
    if len(parts) != 3:
      raise MalformedException('Invalid packet definition, should have 2 parts')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    try:
      timestamp = datetime.fromtimestamp(int(parts[0]), tz=UTC)
    except ValueError as e:
      raise MalformedException('Invalid timestamp, should be an int or float') from e

    try:
      extra = parse_extra(parts[1])
    except Exception as e:
      raise MalformedException('Invalid extra args, cannot be processed') from e

    return PsPacket(timestamp=timestamp, params=extra)

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};'
    raw += f'{cast_extra(self.params)};'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Ps>{raw}{crc}</Ps>'

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
