"""Pb Packet"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field

from layrz_protocol.packets.definitions.ble_advertisement import BleAdvertisement
from layrz_protocol.utils.crc import calculate_crc
from layrz_protocol.utils.exceptions import CrcException, MalformedException

from .base import ClientPacket


class PbPacket(ClientPacket):
  """Pb packet definition"""

  advertisements: list[BleAdvertisement] = Field(default_factory=list, description='List of BLE advertisements')

  @staticmethod
  def from_packet(raw: str) -> 'PbPacket':
    """Creates a BleAdvertisement from a raw message following this structure:
    MAC_ADDRESS;UNIX;LAT;LNG;ALT;MODEL;RSSI;MANUFACTURER+DATA;SERVICE+DATA;CRC16"""
    if not raw.startswith('<Pb>') or not raw.endswith('</Pb>'):
      raise MalformedException('Invalid packet definition, should be <Pb>...</Pb>')
    parts = raw[4:-5].split(';')
    if not parts or (len(parts[:-1]) % 12) != 0:
      raise MalformedException(f'Invalid packet definition - invalid number of parts {len(parts)} - {parts}')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    advertisements: list[BleAdvertisement] = [
      BleAdvertisement.from_packet(';'.join(parts[i : i + 12])) for i in range(0, len(parts[:-1]), 12)
    ]

    return PbPacket(advertisements=advertisements)

  def to_packet(self: Self) -> str:
    """Convert the packet to raw data"""
    raw = ';'.join(
      [
        ';'.join([data.to_packet() for data in self.advertisements]),
      ]
    )
    raw += ';'
    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Pb>{raw}{crc}</Pb>'

  def __str__(self: Self) -> str:
    """Return the string representation of the packet"""
    return self.to_packet()
