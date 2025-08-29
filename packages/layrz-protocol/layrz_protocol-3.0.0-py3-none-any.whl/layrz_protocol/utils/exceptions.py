"""Exceptions"""

import sys

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ParseException(Exception):
  def __init__(self: Self, message: str) -> None:
    self.message = message

  def __str__(self: Self) -> str:
    return f'ParseException: {self.message}'


class CrcException(Exception):
  def __init__(
    self,
    message: str,
    received: int,
    calculated: int,
  ) -> None:
    self.message = message
    self.received = received
    self.calculated = calculated

  def __str__(self: Self) -> str:
    return (
      f'{self.message} - '
      f'Expected: {str(hex(self.calculated))[2:].upper().zfill(4)}, '
      f'Received: {str(hex(self.received))[2:].upper().zfill(4)}'
    )


class CommandException(Exception):
  def __init__(self: Self, message: str) -> None:
    self.message = message

  def __str__(self: Self) -> str:
    return self.message


class ServerException(Exception):
  def __init__(self: Self, message: str) -> None:
    self.message = message

  def __str__(self: Self) -> str:
    return self.message


class MalformedException(Exception):
  def __init__(self: Self, message: str) -> None:
    self.message = message

  def __str__(self: Self) -> str:
    return self.message


class UnimplementedException(Exception):
  def __init__(self: Self, message: str) -> None:
    self.message = message

  def __str__(self: Self) -> str:
    return self.message
