"""Ac Packet"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.packets.definitions.command import Command
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import ServerPacket


class AcPacket(ServerPacket):
  """Ac packet definition"""

  commands: list[Command] = Field(default_factory=list, description='List of commands')

  @staticmethod
  def from_packet(raw: str) -> 'AcPacket':
    """Create a packet from raw data"""
    if not raw.startswith('<Ac>') or not raw.endswith('</Ac>'):
      raise MalformedException('Invalid packet definition, should be <Ac>...</Ac>')

    parts = raw[4:-5].split(';')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    parts = parts[:-1]
    if len(parts) % 4 != 0:
      raise MalformedException('Invalid packet definition, should have 4 parts at least')

    try:
      commands = Command.from_packets(';'.join(parts))
    except Exception as e:
      raise MalformedException('Invalid command definition') from e

    return AcPacket(commands=commands)

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = ';'.join([command.to_packet() for command in self.commands]) + ';'
    crc = str(hex(calculate_crc(raw.encode())))[2:].upper().zfill(4)

    return f'<Ac>{raw}{crc}</Ac>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
