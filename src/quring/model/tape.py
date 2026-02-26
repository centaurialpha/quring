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

from dataclasses import dataclass

from quring.model.transition import BLANK


@dataclass(frozen=True)
class TapeSnapshot:
    """
    Immutable capture of the tape state at a specific moment.
    Used by the simulation history to allow stepping backward.
    """

    cells: dict[int, str]
    head_position: int

    def read(self, position: int) -> str:
        return self.cells.get(position, BLANK)


class Tape:
    """
    A two-way infinite tape represented as a sparse dictionary.

    Unwritten positions implicitly conta
    """

    def __init__(self) -> None:
        self._cells: dict[int, str] = {}
        self._head: int = 0

    @property
    def head_position(self) -> int:
        return self._head

    def seek(self, position: int) -> None:
        """Move the head to an arbitrary position (used for reset/restore)."""
        self._head = position

    def read(self) -> str:
        """Read the symbol under the head."""
        return self._cells.get(self._head, BLANK)

    def write(self, symbol: str) -> None:
        """Write a symbol at the current head position."""
        if symbol == BLANK:
            # Keep the dict sparse: remove explicit blanks
            self._cells.pop(self._head, None)
        else:
            self._cells[self._head] = symbol

    def move_left(self) -> None:
        self._head -= 1

    def move_right(self) -> None:
        self._head += 1

    def set_content(self, text: str, start: int = 0) -> None:
        """
        Write a string onto the tape starting at `start`.
        The head is moved to `start` after writing.
        """
        for index, char in enumerate(text):
            position = start + index
            if char == BLANK:
                self._cells.pop(position, None)
            else:
                self._cells[position] = char
        self._head = start

    def snapshot(self) -> TapeSnapshot:
        """Return an immutable copy of the current tape state."""
        return TapeSnapshot(cells=dict(self._cells), head_position=self._head)

    def restore(self, snapshot: TapeSnapshot) -> None:
        """Restore the tape to a previously captured snapshot."""
        self._cells = dict(snapshot.cells)
        self._head = snapshot.head_position

    def written_range(self) -> tuple[int, int] | None:
        """
        Return (min_pos, max_pos) of all explicitly written cells.
        Returns None if the tape is empty.
        """
        if not self._cells:
            return None
        return min(self._cells), max(self._cells)

    def as_string(self, padding: int = 2) -> str:
        """
        Render the tape as a human-readable string for debugging.
        Shows the written range plus `padding` blanks on each side.
        Marks the head position with square brackets.
        """

        w_range = self.written_range()
        if w_range is None:
            lo, hi = -padding, padding
        else:
            lo, hi = w_range[0] - padding, w_range[1] + padding

        parts = []
        for position in range(lo, hi + 1):
            symbol = self._cells.get(position, BLANK)
            if position == self._head:
                parts.append(f"({symbol})")
            else:
                parts.append(f" {symbol} ")
        return "".join(parts)

    def __repr__(self) -> str:
        return f"Tape(head={self._head}, cells={self._cells!r})"
