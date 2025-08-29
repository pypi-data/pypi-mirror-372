"""Pc Packet"""

import sys
from datetime import datetime
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


from pydantic import Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException

from .base import ClientPacket


class PcPacket(ClientPacket):
  """Pc packet definition"""

  timestamp: datetime = Field(description='Timestamp of the packet', default_factory=lambda: datetime.now(tz=UTC))
  command_id: int = Field(..., description='Command ID')
  message: str = Field(..., description='Message')

  @staticmethod
  def from_packet(raw: str) -> 'PcPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Pc>') or not raw.endswith('</Pc>'):
      raise MalformedException('Invalid packet definition, should be <Pc>...</Pc>')

    parts = raw[4:-5].split(';')
    if len(parts) != 4:
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
      command_id = int(parts[1])
    except ValueError as e:
      raise MalformedException('Invalid command_id, should be an int') from e

    return PcPacket(
      timestamp=timestamp,
      command_id=command_id,
      message=parts[2],
    )

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};{self.command_id};{self.message};'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pc>{raw}{crc}</Pc>'

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
