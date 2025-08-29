"""Pi Packet"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.packets.definitions import FirmwareBranch
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ClientPacket


class PiPacket(ClientPacket):
  """Pi packet definition"""

  ident: str = Field(..., description='IMEI or Unique identifier of the device')
  firmware_id: int | str = Field(..., description='Firmware ID')
  firmware_build: int = Field(..., description='Firmware build number')
  device_id: int = Field(..., description='Device ID')
  hardware_id: int = Field(..., description='Hardware ID')
  model_id: int = Field(..., description='Model ID')
  fota_enabled: bool = Field(..., description='FOTA enabled')
  firmware_branch: FirmwareBranch = Field(default=FirmwareBranch.STABLE, description='Firmware branch')

  @staticmethod
  def from_packet(raw: str) -> 'PiPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Pi>') or not raw.endswith('</Pi>'):
      raise MalformedException('Invalid packet definition, should be <Pi>...</Pi>')

    parts = raw[4:-5].split(';')
    if len(parts) != 9:
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
      firmware_build = int(parts[2])
    except ValueError as e:
      raise MalformedException('Invalid firmware build number') from e

    fota_enabled = parts[7].lower() == 'true' or parts[7] == '1'

    try:
      device_id = int(parts[3])
    except ValueError as e:
      raise MalformedException('Invalid device_id, should be an int') from e

    try:
      hardware_id = int(parts[4])
    except ValueError as e:
      raise MalformedException('Invalid hardware_id, should be an int') from e

    try:
      model_id = int(parts[5])
    except ValueError as e:
      raise MalformedException('Invalid model_id, should be an int') from e

    firmware_id: int | str
    try:
      firmware_id = int(parts[1])
    except ValueError:
      firmware_id = parts[1]

    try:
      firmware_branch = FirmwareBranch(int(parts[6]))
    except ValueError:
      firmware_branch = FirmwareBranch.STABLE

    return PiPacket(
      ident=parts[0],
      firmware_id=firmware_id,
      firmware_build=firmware_build,
      device_id=device_id,
      hardware_id=hardware_id,
      model_id=model_id,
      firmware_branch=firmware_branch,
      fota_enabled=fota_enabled,
    )

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{self.ident};'
    raw += f'{self.firmware_id};'
    raw += f'{self.firmware_build};'
    raw += f'{self.device_id};'
    raw += f'{self.hardware_id};'
    raw += f'{self.model_id};'
    raw += f'{self.firmware_branch.value};'
    raw += f'{"1" if self.fota_enabled else "0"};'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pi>{raw}{crc}</Pi>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
