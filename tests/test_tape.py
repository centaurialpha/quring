# Copyright 2026 - Gabriel Acosta <acostadariogabriel@gmail.com>
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

import pytest

from quring.model.tape import Tape
from quring.model.transition import BLANK


@pytest.fixture
def tape() -> Tape:
    return Tape()


@pytest.fixture
def tape_abc(tape: Tape) -> Tape:
    tape.set_content("abc")
    return tape


def test_unwritten_cell_returns_blank(tape):
    assert tape.read() == BLANK


@pytest.mark.parametrize("symbol", ["a", "b", "0", "1", "A", "X", "#"])
def test_write_and_read(tape, symbol):
    tape.write(symbol)
    assert tape.read() == symbol


@pytest.mark.parametrize("symbol", ["a", "b", "Z"])
def test_write_blank_after_write_keeps_tape_sparse(tape, symbol):
    tape.write(symbol)
    tape.write(BLANK)
    assert tape._cells == {}


@pytest.mark.parametrize(
    "steps, expected_pos",
    [
        (1, 1),
        (3, 3),
        (10, 10),
    ],
)
def test_move_right(tape, steps, expected_pos):
    for _ in range(steps):
        tape.move_right()
    assert tape.head_position == expected_pos


@pytest.mark.parametrize(
    "steps, expected_pos",
    [
        (1, -1),
        (3, -3),
        (10, -10),
    ],
)
def test_move_left(tape, steps, expected_pos):
    for _ in range(steps):
        tape.move_left()
    assert tape.head_position == expected_pos


@pytest.mark.parametrize("position", [-5, 0, 1, 100])
def test_seek(tape, position):
    tape.seek(position)
    assert tape.head_position == position


def test_read_after_interleaved_writes(tape):
    tape.write("a")
    tape.move_right()
    tape.write("b")
    tape.seek(0)
    assert tape.read() == "a"
    tape.move_right()
    assert tape.read() == "b"


@pytest.mark.parametrize(
    "content, start, expected_at_start",
    [
        ("abc", 0, "a"),
        ("xyz", 3, "x"),
        ("01", -2, "0"),
    ],
)
def test_set_content_head_and_first_symbol(tape, content, start, expected_at_start):
    tape.set_content(content, start=start)
    assert tape.head_position == start
    assert tape.read() == expected_at_start


@pytest.mark.parametrize(
    "content, expected_cells",
    [
        ("ab", {0: "a", 1: "b"}),
        (f"a{BLANK}b", {0: "a", 2: "b"}),  # blank in the middle stays sparse
    ],
)
def test_set_content_cell_layout(tape, content, expected_cells):
    tape.set_content(content)
    assert tape._cells == expected_cells


def test_clear_empties_cells_and_resets_head(tape_abc):
    tape_abc.move_right()
    tape_abc.clear()
    assert tape_abc._cells == {}
    assert tape_abc.head_position == 0
    assert tape_abc.read() == BLANK


def test_snapshot_is_independent_of_later_writes(tape):
    tape.set_content("ab")
    snap = tape.snapshot()
    tape.write("x")
    assert snap.read(0) == "a"


@pytest.mark.parametrize(
    "content, seek_to",
    [
        ("ab", 0),
        ("xyz", 2),
    ],
)
def test_restore_returns_to_snapshotted_state(tape, content, seek_to):
    tape.set_content(content)
    tape.seek(seek_to)
    snap = tape.snapshot()

    tape.set_content("overwritten")
    tape.restore(snap)

    assert tape.head_position == seek_to
    assert tape.read() == content[seek_to]


@pytest.mark.parametrize("move_to", [0, 1, 3, -2])
def test_snapshot_captures_head_position(tape, move_to):
    tape.seek(move_to)
    snap = tape.snapshot()
    assert snap.head_position == move_to


def test_written_range_empty_tape(tape):
    assert tape.written_range() is None


@pytest.mark.parametrize(
    "content, start, expected_lo, expected_hi",
    [
        ("abc", 0, 0, 2),
        ("abc", -1, -1, 1),
        ("xy", 5, 5, 6),
    ],
)
def test_written_range(tape, content, start, expected_lo, expected_hi):
    tape.set_content(content, start=start)
    result = tape.written_range()
    assert result is not None
    lo, hi = result
    assert lo == expected_lo
    assert hi == expected_hi


@pytest.mark.parametrize("symbol", ["a", "0", "#"])
def test_as_string_marks_head_symbol(tape, symbol):
    tape.write(symbol)
    assert f"[{symbol}]" in tape.as_string(padding=0)
