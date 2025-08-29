"""Firmware branch"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class FirmwareBranch(Enum):
  """Firmware branches"""

  STABLE = 0
  DEVELOPMENT = 1

  def __str__(self: Self) -> str:
    return self.name

  def __repr__(self: Self) -> str:
    return f'FiirmwareBranch.{self.name}'
