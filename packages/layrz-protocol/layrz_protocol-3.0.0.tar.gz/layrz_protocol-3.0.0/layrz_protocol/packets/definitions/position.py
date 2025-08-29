"""Position packet"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

_PositionType = type['Position']


class Position(BaseModel):
  """Position information packet"""

  latitude: float | None = Field(default=None, description='Defines the latitude of the device')
  longitude: float | None = Field(default=None, description='Defines the longitude of the device')
  altitude: float | None = Field(default=None, description='Defines the altitude of the device')
  speed: float | None = Field(default=None, description='Defines the speed of the device')
  direction: float | None = Field(default=None, description='Defines the direction of the device')
  satellites: int | None = Field(default=None, description='Defines the number of satellites')
  hdop: float | None = Field(default=None, description='Defines the HDOP of the device')

  @field_validator('latitude', mode='before')
  @classmethod
  def _validate_latitude(cls: _PositionType, latitude: Any) -> float | None:
    if latitude is None:
      return None

    if not isinstance(latitude, float):
      raise ValueError('latitude should be a float')

    if not -90 <= latitude <= 90:
      raise ValueError('latitude should be between -90 and 90')

    return latitude

  @field_validator('longitude', mode='before')
  @classmethod
  def _validate_longitude(cls: _PositionType, longitude: Any) -> float | None:
    if longitude is None:
      return None

    if not isinstance(longitude, float):
      raise ValueError('longitude should be a float')

    if not -180 <= longitude <= 180:
      raise ValueError('longitude should be between -180 and 180')

    return longitude

  @field_validator('direction', mode='before')
  @classmethod
  def _validate_direction(cls: _PositionType, direction: Any) -> float | None:
    if direction is None:
      return None

    if not isinstance(direction, (int, float)):
      raise ValueError('direction should be a float')

    if isinstance(direction, int):
      direction = float(direction)

    if not 0 <= direction <= 360:
      raise ValueError('direction should be between 0 and 360')

    return direction

  @field_validator('hdop', mode='before')
  @classmethod
  def _validate_hdop(cls: _PositionType, hdop: Any) -> float | None:
    if hdop is None:
      return None

    if not isinstance(hdop, float):
      raise ValueError('hdop should be a float')

    if hdop < 0:
      raise ValueError('hdop should be a positive number')

    return hdop
