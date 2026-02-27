# Copyright 2019-2026 - Gabriel Acosta <acostadariogabriel@gmail.com>
#
# This file is part of Pireal.
#
# Pireal is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Pireal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pireal; If not, see <http://www.gnu.org/licenses/>.

from enum import (
    Enum,
    auto,
)


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


class StateType(Enum):
    INITIAL = auto()
    NORMAL = auto()
    FINAL = auto()


class MachineStatus(Enum):
    IDLE = auto()
    RUNNING = auto()
    ACCEPTED = auto()
    JAMMED = auto()

    @property
    def is_terminal(self) -> bool:
        """True if the machine can no longer advance (accepted or jammed)."""
        return self in (MachineStatus.ACCEPTED, MachineStatus.JAMMED)
