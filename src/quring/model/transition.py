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
    field,
)

from quring.model.types import Direction, Point

BLANK = "#"


@dataclass(frozen=True)
class TransitionFunction:
    """
    A single rule within a transition: read a symbol, write a symbol, move.

    frozen=True makes it hashable and safe to use in sets if needed.
    """

    read: str
    write: str
    move: Direction

    def __repr__(self) -> str:
        arrow = "L" if self.move == Direction.LEFT else "R"
        return f"({self.read!r} -> {self.write!r}, {arrow})"


@dataclass
class Transition:
    """
    A directed edge between two states.

    One Transition can carry multiple TransitionFunctions, which represent
    different symbols that all trigger the same arc (drawn as a single arrow
    in the editor, with multiple labels).
    """

    from_state: int
    to_state: int
    functions: list[TransitionFunction] = field(default_factory=list)

    # Control point for the bezier curve in the editor.
    # (0.0, 0.0) means the view will calculate a default midpoint.
    control_point: Point = field(default_factory=Point)

    @property
    def is_self_loop(self) -> bool:
        return self.from_state == self.to_state

    def match(self, symbol: str) -> TransitionFunction | None:
        """Return the first function that reads `symbol`, or None."""
        for function in self.functions:
            if function.read == symbol:
                return function
        return None

    def __repr__(self) -> str:
        return f"Transition({self.from_state} -> {self.to_state}, functions={self.functions!r})"
