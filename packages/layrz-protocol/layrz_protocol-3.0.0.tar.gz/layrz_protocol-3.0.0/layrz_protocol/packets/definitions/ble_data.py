"""Ble data"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel, Field

from layrz_protocol.utils.exceptions import MalformedException, ParseException


class BleData(BaseModel):
  mac_address: str = Field(..., description='Defines the MAC address of the device')
  model: str = Field(..., description='Defines the model of the device')

  @staticmethod
  def from_packets(raw: str) -> list['BleData']:
    parts = raw.split(';')

    if not parts:
      return []

    if len(parts) == 1:
      return []

    devices = []

    for part in parts:
      subparts = part.strip().split(':')
      if len(subparts) != 2:
        raise ParseException('Invalid BLE Data, should be in the format MAC_ADDRESS:MODEL')
      raw_mac_address = subparts[0]

      if len(raw_mac_address) != 12:
        raise MalformedException('Invalid MAC Address')
      mac_address: str = ':'.join([raw_mac_address[i : i + 2] for i in range(0, 12, 2)])

      model = subparts[1]

      devices.append(
        BleData(
          mac_address=mac_address,
          model=model,
        )
      )

    return devices

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    return f'{self.mac_address.replace(":", "").upper()}:{self.model}'
