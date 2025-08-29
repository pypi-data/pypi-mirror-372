"""Ble Manufacturer Data"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel, Field

from layrz_protocol.utils.exceptions import MalformedException


class BleManufacturerData(BaseModel):
  """Ble Manufacturer Data"""

  company_id: int = Field(..., description='Defines the company id')
  data: list[int] = Field(description='Defines the manufacturer data', default_factory=list)

  @staticmethod
  def from_packet(raw: str) -> BleManufacturerData | None:
    """Creates a BleManufacturerData from a raw message following this structure:
    COMPANY_ID:DATA"""
    if not raw:
      return None

    parts = raw.split(':')
    if len(parts) != 2:
      raise MalformedException('Invalid packet definition')

    try:
      company_id: int = int(parts[0], base=16)
    except ValueError as e:
      raise MalformedException('Invalid company id, should be an int') from e

    data: list[int] = []
    while parts[1]:
      data.append(int(parts[1][:2], base=16))
      parts[1] = parts[1][2:]

    return BleManufacturerData(company_id=company_id, data=data)

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    output = f'{self.company_id:04X}:'
    output += ''.join([f'{byte:02X}' for byte in self.data])
    return output
