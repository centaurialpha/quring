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

from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import (
    Transition,
    TransitionFunction,
)
from quring.model.types import (
    Direction,
    StateType,
)


@pytest.fixture
def machine() -> TuringMachine:
    """
    Minimal machine that accepts "ab":
        q0 --(a/A, R)--> q1 --(b/B, R)--> q2 (final)
    """
    m = TuringMachine()
    m.add_state(State(id=0, name="q0", state_type=StateType.INITIAL))
    m.add_state(State(id=1, name="q1", state_type=StateType.NORMAL))
    m.add_state(State(id=2, name="q2", state_type=StateType.FINAL))
    m.add_transition(
        Transition(
            from_state=0,
            to_state=1,
            functions=[TransitionFunction(read="a", write="A", move=Direction.RIGHT)],
        )
    )
    m.add_transition(
        Transition(
            from_state=1,
            to_state=2,
            functions=[TransitionFunction(read="b", write="B", move=Direction.RIGHT)],
        )
    )
    return m


@pytest.fixture
def ready(machine: TuringMachine) -> TuringMachine:
    """Machine with 'ab' on the tape and reset called."""
    machine.tape.set_content("ab")
    machine.reset()
    return machine


@pytest.mark.parametrize(
    "state_id, name, state_type",
    [
        (0, "q0", StateType.INITIAL),
        (1, "q1", StateType.NORMAL),
        (5, "qf", StateType.FINAL),
    ],
)
def test_add_and_get_state(state_id, name, state_type):
    m = TuringMachine()
    s = State(id=state_id, name=name, state_type=state_type)
    m.add_state(s)
    assert m.get_state(state_id) is s


@pytest.mark.parametrize("duplicate_id", [0, 1, 2])
def test_add_duplicate_state_raises(duplicate_id):
    m = TuringMachine()
    m.add_state(State(id=duplicate_id, name="original"))
    with pytest.raises(ValueError, match="already exists"):
        m.add_state(State(id=duplicate_id, name="duplicate"))


@pytest.mark.parametrize(
    "state_to_remove, surviving_transitions_from",
    [
        # remove q0 (INITIAL) → only 0→1 disappears; 1→2 is unaffected
        (0, {0: [], 1: [2], 2: []}),
        # remove q1 (middle) → both 0→1 and 1→2 disappear (q1 is in both)
        (1, {0: [], 1: [], 2: []}),
        # remove q2 (FINAL)  → only 1→2 disappears; 0→1 survives
        (2, {0: [1], 1: [], 2: []}),
    ],
)
def test_remove_state_also_removes_its_transitions(machine, state_to_remove, surviving_transitions_from):
    machine.remove_state(state_to_remove)
    assert machine.get_state(state_to_remove) is None
    for from_id, expected_targets in surviving_transitions_from.items():
        targets = [t.to_state for t in machine.get_transitions_from(from_id)]
        assert targets == expected_targets


def test_get_initial_state(machine):
    initial = machine.get_initial_state()
    assert initial is not None
    assert initial.id == 0


def test_get_initial_state_returns_none_when_absent():
    m = TuringMachine()
    assert m.get_initial_state() is None


@pytest.mark.parametrize("n_ids", [1, 5, 20])
def test_next_id_produces_unique_values(machine, n_ids):
    ids = [machine.next_id() for _ in range(n_ids)]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "state_type, expected_property, expected_value",
    [
        (StateType.INITIAL, "is_initial", True),
        (StateType.FINAL, "is_final", True),
        (StateType.NORMAL, "is_normal", True),
        (StateType.INITIAL, "is_final", False),
        (StateType.FINAL, "is_initial", False),
        (StateType.NORMAL, "is_final", False),
    ],
)
def test_state_type_predicates(state_type, expected_property, expected_value):
    s = State(id=0, name="q", state_type=state_type)
    assert getattr(s, expected_property) == expected_value
