"""Base packet definitions"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import BaseModel

from layrz_protocol.utils.exceptions import UnimplementedException


class Packet(BaseModel):
  """Main packet class"""

  @staticmethod
  def from_packet(raw: str) -> 'Packet':
    """Create a packet from raw data"""
    raise UnimplementedException('Method not implemented')

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raise UnimplementedException('Method not implemented')

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()
