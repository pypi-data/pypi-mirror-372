"""Ble"""

import sys
from datetime import datetime
from typing import Any, TypeAlias

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.packets.definitions.ble_manufacturer_data import BleManufacturerData
from layrz_protocol.packets.definitions.ble_service_data import BleServiceData
from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException

_BleAdvertisementType: TypeAlias = type['BleAdvertisement']


class BleAdvertisement(BaseModel):
  """Ble Advertisement"""

  mac_address: str = Field(..., description='Defines the MAC address of the device')
  timestamp: datetime = Field(
    description='Defines the timestamp of the packet',
    default_factory=lambda: datetime.now(tz=UTC),
  )
  latitude: float | None = Field(default=None, description='Defines the latitude of the device')
  longitude: float | None = Field(default=None, description='Defines the longitude of the device')
  altitude: float | None = Field(default=None, description='Defines the altitude of the device')
  model: str = Field(..., description='Defines the model of the device')
  device_name: str | None = Field(default=None, description='Defines the name of the device')
  rssi: int = Field(default=0, description='Defines the RSSI of the device')
  tx_power: int | None = Field(default=None, description='Defines the TX Power of the device')
  manufacturer_data: list[BleManufacturerData] = Field(
    description='Defines the manufacturer data of the device',
    default_factory=list,
  )
  service_data: list[BleServiceData] = Field(
    description='Defines the service data of the device',
    default_factory=list,
  )

  @staticmethod
  def from_packet(raw: str) -> 'BleAdvertisement':
    """Initialize the packet"""
    parts = raw.split(';')
    if len(parts) != 12:
      raise MalformedException('Invalid packet definition')

    (
      raw_mac_address,
      raw_timestamp,
      raw_latitude,
      raw_longitude,
      raw_altitude,
      raw_model,
      raw_device_name,
      raw_rssi,
      raw_tx_power,
      raw_manufacturer_data,
      raw_service_data,
      raw_crc,
    ) = parts

    received_crc: int
    try:
      received_crc = int(raw_crc, base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    if len(raw_mac_address) != 12:
      raise MalformedException('Invalid MAC Address')

    mac_address: str = ':'.join([raw_mac_address[i : i + 2] for i in range(0, 12, 2)])

    try:
      timestamp: datetime = datetime.fromtimestamp(int(raw_timestamp), tz=UTC)
    except ValueError as e:
      raise MalformedException('Invalid timestamp, should be an int or float') from e

    try:
      latitude: float | None = float(raw_latitude) if raw_latitude else None
    except ValueError as e:
      raise MalformedException('Invalid latitude, should be a float') from e

    try:
      longitude: float | None = float(raw_longitude) if raw_longitude else None
    except ValueError as e:
      raise MalformedException('Invalid longitude, should be a float') from e

    try:
      altitude: float | None = float(raw_altitude) if raw_altitude else None
    except ValueError as e:
      raise MalformedException('Invalid altitude, should be a float') from e

    try:
      rssi: int = int(raw_rssi)
    except ValueError as e:
      raise MalformedException('Invalid RSSI, should be an int') from e

    try:
      tx_power: int | None = int(raw_tx_power) if raw_tx_power else None
    except ValueError as e:
      raise MalformedException('Invalid TX Power, should be an int') from e

    pre_manufacturer_data: list[BleManufacturerData | None] = [
      BleManufacturerData.from_packet(part) for part in raw_manufacturer_data.split(',')
    ] or []

    manufacturer_data = [mf for mf in pre_manufacturer_data if mf]

    pre_service_data: list[BleServiceData | None] = [
      BleServiceData.from_packet(part) for part in raw_service_data.split(',')
    ] or []
    service_data = [sd for sd in pre_service_data if sd]

    return BleAdvertisement(
      device_name=raw_device_name,
      mac_address=mac_address,
      timestamp=timestamp,
      latitude=latitude,
      longitude=longitude,
      altitude=altitude,
      model=raw_model,
      rssi=rssi,
      tx_power=tx_power,
      manufacturer_data=manufacturer_data,
      service_data=service_data,
    )

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    raw = ';'.join(
      [
        self.mac_address.replace(':', ''),
        str(int(self.timestamp.timestamp())),
        str(self.latitude) if self.latitude is not None else '',
        str(self.longitude) if self.longitude is not None else '',
        str(self.altitude) if self.altitude is not None else '',
        self.model,
        self.device_name if self.device_name is not None else '',
        str(self.rssi),
        str(self.tx_power) if self.tx_power is not None else '',
        ','.join([data.to_packet() for data in self.manufacturer_data]),
        ','.join([data.to_packet() for data in self.service_data]),
      ]
    )
    raw += ';'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'{raw}{crc}'

  @field_validator('timestamp', mode='before')
  @classmethod
  def _validate_datetime(cls: _BleAdvertisementType, value: Any) -> datetime:
    """Validate the timestamp"""
    if not isinstance(value, (datetime, int)):
      return datetime.now(tz=UTC)

    if isinstance(value, int):
      return datetime.fromtimestamp(value, tz=UTC)

    return value

  @field_validator('latitude', mode='before')
  @classmethod
  def _validate_latitude(cls: _BleAdvertisementType, value: Any) -> float | None:
    """Validate the latitude"""
    if value is None:
      return value

    if not isinstance(value, float):
      raise ValueError('Invalid latitude, should be a float')

    if value < -90 or value > 90:
      raise ValueError('Invalid latitude, should be between -90 and 90')

    return value

  @field_validator('longitude', mode='before')
  @classmethod
  def _validate_longitude(cls: _BleAdvertisementType, value: Any) -> float | None:
    """Validate the longitude"""
    if value is None:
      return value

    if not isinstance(value, float):
      raise ValueError('Invalid longitude, should be a float')

    if value < -180 or value > 180:
      raise ValueError('Invalid longitude, should be between -180 and 180')

    return value
