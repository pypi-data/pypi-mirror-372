"""Layrz Protocol client"""

import base64
import logging
import sys
from datetime import datetime
from typing import Any

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

import requests

from layrz_protocol.constants import UTC
from layrz_protocol.packets.base import Packet
from layrz_protocol.packets.client import ClientPacket, PdPacket
from layrz_protocol.packets.definitions import Position
from layrz_protocol.packets.server import AbPacket, AcPacket, AoPacket, ArPacket, ServerPacket
from layrz_protocol.utils import ParseException, ServerException

log = logging.getLogger(__name__)


class LayrzProtocol:
  """
  Layrz Protocol connector
  ---
  Available methods:
    - send_data() : Sends a plain message to the Layrz Network
    - send_sos() : Sends a SOS message to the Layrz Network
    - send_image() : Send an image to Layrz
    - get_commands() : Get commands from Layrz
    - compose_empty_pd() : Compose an empty PdPacket
  """

  def __init__(
    self: Self,
    ident: str,
    base_url: str,
    password: str = '',
  ) -> None:
    """
    Constructor

    :param ident: Device unique identifier, this ident should be created in the Layrz Network
    :param base_url: Layrz Network API URL
    :param password: Device password, normally is an empty string, but can be set to a custom value in Layrz
    """
    self.ident = ident
    self.password = password
    self.base_url = base_url

  @property
  def headers(self: Self) -> dict[str, Any]:
    """
    Headers

    :return: The headers to use in the requests
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    return {
      'Content-Type': 'text/plain',
      'Authorization': f'LayrzAuth {self.ident};{self.password}',
    }

  def send_data(self: Self, packet: ClientPacket) -> ServerPacket:
    """
    Sends a plain message to the Layrz Network

    :param packet: Packet to send
    :return: Response packet from the server
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    return self._send_to_layrz(packet)

  def send_sos(self: Self, message: PdPacket | None = None) -> ServerPacket:
    """
    Sends a SOS message to the Layrz Network

    :param message: Message to send, if None, an empty message will be sent
    :return: Response packet from the server
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    if message is None or not isinstance(message, PdPacket):
      message = self.compose_empty_pd()

    extra = message.extra.copy()
    extra['alarm.event'] = True

    return self._send_to_layrz(
      PdPacket(
        timestamp=message.timestamp,
        position=message.position,
        extra=extra,
      )
    )

  def send_image(
    self: Self,
    content: bytes,
    filename: str,
    content_type: str = 'image/jpeg',
  ) -> ServerPacket:
    """
    Send an image to Layrz

    :param content: Image content
    :param filename: Image filename
    :param content_type: Image content type
    :return: Response packet from the server
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """

    if ' ' in filename:
      filename = filename.replace(' ', '_')
    if '/' in filename:
      filename = filename.replace('/', '_')
    if '.' in filename:
      filename = filename.replace('.', '_')

    base64_bytes = base64.b64encode(content)

    casted_base64 = f'data:{content_type};base64,{base64_bytes.decode()}'

    response = requests.post(
      f'{self.base_url}/image/{filename}',
      headers=self.headers,
      data=casted_base64,
    )

    return self._process_response(response)

  def get_commands(self: Self) -> ServerPacket:
    """
    Get commands from Layrz

    :return: Response packet
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    response = requests.get(
      f'{self.base_url}/commands',
      headers=self.headers,
    )

    return self._process_response(response)

  def get_ble(self: Self) -> ServerPacket:
    """
    Get BLE devices from Layrz

    :return: Response packet
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    response = requests.get(
      f'{self.base_url}/ble',
      headers=self.headers,
    )

    return self._process_response(response)

  def _send_to_layrz(self: Self, packet: ClientPacket) -> ServerPacket:
    """
    Send to Layrz

    :param packet: Packet to send
    :return: Response packet from the server
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    response = requests.post(
      f'{self.base_url}/message',
      headers=self.headers,
      data=packet.to_packet(),
    )

    return self._process_response(response)

  def _process_response(self: Self, response: requests.Response) -> ServerPacket:
    """
    Process response

    :param response: Response from the server
    :return: Response packet from the server
    :raises ParseException: If the response is not valid
    :raises ServerException: If the server returns an error
    :raises Exception: If the response is not valid
    :raises ValueError: If the response is not valid
    """
    if response.status_code == 500:
      raise ServerException('Internal server error')

    log.debug('Response: %s', response.text)

    raw = response.text
    if raw.startswith('<Ao>') and raw.endswith('</Ao>'):
      return AoPacket.from_packet(raw)

    if raw.startswith('<Ac>') and raw.endswith('</Ac>'):
      return AcPacket.from_packet(raw)

    if raw.startswith('<Ar>') and raw.endswith('</Ar>'):
      return ArPacket.from_packet(raw)

    if raw.startswith('<Ab>') and raw.endswith('</Ab>'):
      return AbPacket.from_packet(raw)

    raise ParseException('Invalid packet format')

  def compose_empty_pd(self: Self) -> PdPacket:
    """
    Compose an empty PdPacket
    :return: Empty PdPacket
    """
    return PdPacket(
      timestamp=datetime.now(tz=UTC),
      position=Position(),
      extra={},
    )
