"""Command definition"""

import sys
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel, Field

from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, ParseException
from layrz_protocol.utils.parsers import cast_extra, parse_extra


class Command(BaseModel):
  """Command packet definition"""

  command_id: int = Field(..., description='Command ID')
  command_name: str = Field(..., description='Command name')
  args: dict[str, Any] = Field(description='Command arguments', default_factory=dict)

  @staticmethod
  def from_packets(raw: str) -> list['Command']:
    parts = raw.split(';')

    if not parts:
      return []

    if len(parts) == 1:
      return []

    if len(parts) % 4 != 0:
      raise ParseException('Invalid command definition')

    commands = []

    for i in range(0, len(parts), 4):
      try:
        command_id = int(parts[i])
      except ValueError as e:
        raise ParseException('Invalid command_id, should be an int') from e

      command_name = parts[i + 1]
      raw_args = parts[i + 2]

      try:
        received_crc = int(parts[i + 3], base=16)
      except ValueError as e:
        raise ParseException('Invalid CRC, should be an int') from e

      calculated_crc = calculate_crc(f'{command_id};{command_name};{raw_args};'.encode())

      if received_crc != calculated_crc:
        raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

      args = parse_extra(raw_args)

      commands.append(
        Command(
          command_id=command_id,
          command_name=command_name,
          args=args,
        )
      )

    return commands

  def to_packet(self: Self) -> str:
    payload = f'{self.command_id};{self.command_name};'
    payload += f'{cast_extra(self.args)};'
    crc = str(hex(calculate_crc(payload.encode())))[2:].upper().zfill(4)

    return f'{payload}{crc}'

  def __str__(self: Self) -> str:
    return self.to_packet()
