"""Ble Service data"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel, Field

from layrz_protocol.utils.exceptions import MalformedException


class BleServiceData(BaseModel):
  """Ble Service Data"""

  uuid: int = Field(..., description='Defines the service uuid')
  data: list[int] = Field(description='Defines the service data', default_factory=list)

  @staticmethod
  def from_packet(raw: str) -> BleServiceData | None:
    """Creates a BleServiceData from a raw message following this structure:
    SERVICE_UUID:DATA"""
    if not raw:
      return None

    parts = raw.split(':')
    if len(parts) != 2:
      raise MalformedException(f'Invalid packet definition - invalid number of parts - {len(parts)} - {parts}')

    try:
      service_uuid: int = int(parts[0], base=16)
    except ValueError as e:
      raise MalformedException('Invalid service uuid, should be an int') from e

    data: list[int] = []
    while parts[1]:
      data.append(int(parts[1][:2], base=16))
      parts[1] = parts[1][2:]

    return BleServiceData(uuid=service_uuid, data=data)

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    output = f'{self.uuid:04X}:'
    output += ''.join([f'{byte:02X}' for byte in self.data])
    return output
