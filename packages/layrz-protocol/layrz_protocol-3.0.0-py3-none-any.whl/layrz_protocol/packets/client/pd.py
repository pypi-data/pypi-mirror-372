"""Pd Packet"""

import sys
from datetime import datetime
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


from pydantic import Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.packets.definitions.position import Position
from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException
from layrz_protocol.utils.parsers import cast_extra, parse_extra

from .base import ClientPacket


class PdPacket(ClientPacket):
  """Pd packet definition"""

  timestamp: datetime = Field(description='Timestamp of the packet', default_factory=lambda: datetime.now(tz=UTC))
  position: Position
  extra: dict[str, Any] = {}

  @staticmethod
  def from_packet(raw: str) -> 'PdPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Pd>') or not raw.endswith('</Pd>'):
      raise MalformedException('Invalid packet definition, should be <Pd>...</Pd>')

    parts = raw[4:-5].split(';')
    if len(parts) != 10:
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

    latitude: float | None = None
    if parts[1]:
      try:
        latitude = float(f'{parts[1]}')
      except ValueError as e:
        raise MalformedException('Invalid latitude, should be a float') from e

    longitude: float | None = None
    if parts[2]:
      try:
        longitude = float(f'{parts[2]}')
      except ValueError as e:
        raise MalformedException('Invalid longitude, should be a float') from e

    altitude: float | None = None
    if parts[3]:
      try:
        altitude = float(f'{parts[3]}')
      except ValueError as e:
        raise MalformedException('Invalid altitude, should be a float') from e

    speed: float | None = None
    if parts[4]:
      try:
        speed = float(f'{parts[4]}')
      except ValueError as e:
        raise MalformedException('Invalid speed, should be a float') from e

    direction: float | None = None
    if parts[5]:
      try:
        direction = float(f'{parts[5]}')
      except ValueError as e:
        raise MalformedException('Invalid direction, should be a float') from e

    satellites: int | None = None
    if parts[6]:
      try:
        satellites = int(f'{parts[6]}')
      except ValueError as e:
        raise MalformedException('Invalid satellites, should be an int') from e

    hdop: float | None = None
    if parts[7]:
      try:
        hdop = float(f'{parts[7]}')
      except ValueError as e:
        raise MalformedException('Invalid hdop, should be a float') from e

    try:
      position = Position(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        speed=speed,
        direction=direction,
        satellites=satellites,
        hdop=hdop,
      )
    except AssertionError as e:
      raise MalformedException('Invalid position paramter') from e

    try:
      extra = parse_extra(parts[8])
    except Exception as e:
      raise MalformedException('Invalid extra parameters') from e

    return PdPacket(timestamp=timestamp, position=position, extra=extra)

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};'
    if self.position.latitude is None:
      raw += ';'
    else:
      raw += f'{self.position.latitude};'

    if self.position.longitude is None:
      raw += ';'
    else:
      raw += f'{self.position.longitude};'

    if self.position.altitude is None:
      raw += ';'
    else:
      raw += f'{self.position.altitude};'

    if self.position.speed is None:
      raw += ';'
    else:
      raw += f'{self.position.speed};'

    if self.position.direction is None:
      raw += ';'
    else:
      raw += f'{self.position.direction};'

    if self.position.satellites is None:
      raw += ';'
    else:
      raw += f'{self.position.satellites};'

    if self.position.hdop is None:
      raw += ';'
    else:
      raw += f'{self.position.hdop};'

    raw += f'{cast_extra(self.extra)};'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pd>{raw}{crc}</Pd>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()

  @field_validator('timestamp', mode='before')
  def _validate_timestamp(cls: 'PdPacket', value: Any) -> datetime:
    """Validate timestamp"""
    if value is None:
      return datetime.now(tz=UTC)

    if isinstance(value, (int, float)):
      return datetime.fromtimestamp(value, tz=UTC)

    if isinstance(value, datetime):
      return value

    return datetime.fromtimestamp(value, tz=UTC)
