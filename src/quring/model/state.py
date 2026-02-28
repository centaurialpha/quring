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

from dataclasses import (
    dataclass,
)

from quring.model.types import Point, StateType


@dataclass
class State:
    id: int
    name: str
    state_type: StateType = StateType.NORMAL

    # Canvas position — owned by the model so it survives save/load.
    # The view updates these when the user moves a node.
    position: Point = Point()

    # Optional free-text comment shown as a tooltip in the editor.
    comment: str = ""

    @property
    def is_initial(self) -> bool:
        return self.state_type == StateType.INITIAL

    @property
    def is_final(self) -> bool:
        return self.state_type == StateType.FINAL

    @property
    def is_normal(self) -> bool:
        return self.state_type == StateType.NORMAL

    def __repr__(self) -> str:
        return f"State(id={self.id}, name={self.name}, type={self.state_type.name})"
