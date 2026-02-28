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
from PySide6.QtGui import QUndoStack

from quring.controllers.command import (
    AddStateCommand,
    AddTransitionCommand,
    EditStateCommand,
    EditTransitionCommand,
    MoveControlPointCommand,
    MoveStateCommand,
    RemoveStateCommand,
    RemoveTransitionCommand,
)
from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import Transition, TransitionFunction
from quring.model.types import Direction, Point, StateType


@pytest.fixture
def stack(qapp) -> QUndoStack:
    return QUndoStack()


@pytest.fixture
def machine() -> TuringMachine:
    machine = TuringMachine()
    machine.add_state(State(id=0, name="q0", state_type=StateType.INITIAL, position=Point(0, 0)))
    machine.add_state(State(id=1, name="q1", state_type=StateType.NORMAL, position=Point(100, 0)))
    machine.add_state(State(id=2, name="q2", state_type=StateType.FINAL, position=Point(200, 0)))
    machine.add_transition(
        Transition(
            from_state=0,
            to_state=1,
            functions=[TransitionFunction("a", "A", Direction.RIGHT)],
        )
    )
    return machine


def test_add_state_redo(stack, machine):
    state = State(id=3, name="q3", state_type=StateType.NORMAL)
    stack.push(AddStateCommand(machine, state))
    assert machine.get_state(3) is state


def test_add_state_undo(stack, machine):
    state = State(id=3, name="q3", state_type=StateType.NORMAL)
    stack.push(AddStateCommand(machine, state))
    stack.undo()
    assert machine.get_state(3) is None


@pytest.mark.parametrize(
    "state_id, expected_remaining",
    [
        (0, [1, 2]),
        (1, [0, 2]),
        (2, [0, 1]),
    ],
)
def test_remove_state_redo(stack, machine, state_id, expected_remaining):
    stack.push(RemoveStateCommand(machine, state_id))
    assert machine.get_state(state_id) is None
    for sid in expected_remaining:
        assert machine.get_state(sid) is not None


@pytest.mark.parametrize("state_id", [0, 1, 2])
def test_remove_state_undo_restores_state(stack, machine, state_id):
    original = machine.get_state(state_id)
    stack.push(RemoveStateCommand(machine, state_id))
    stack.undo()
    assert machine.get_state(state_id) == original


def test_remove_state_undo_restores_affected_transitions(stack, machine):
    # Transition 0→1 exists; removing state 0 should take it with it.
    stack.push(RemoveStateCommand(machine, 0))
    assert machine.get_transitions_from(0) == []
    stack.undo()
    assert len(machine.get_transitions_from(0)) == 1


@pytest.mark.parametrize("new_pos", [Point(50, 75), Point(-10, 200), Point(0, 0)])
def test_move_state_redo(stack, machine, new_pos):
    stack.push(MoveStateCommand(machine, 0, Point(0, 0), new_pos))
    assert machine.get_state(0).position == new_pos


@pytest.mark.parametrize(
    "old_pos, new_pos",
    [
        (Point(0, 0), Point(50, 75)),
        (Point(10, 20), Point(100, 200)),
    ],
)
def test_move_state_undo(stack, machine, old_pos, new_pos):
    machine.get_state(0).position = old_pos
    stack.push(MoveStateCommand(machine, 0, old_pos, new_pos))
    stack.undo()
    assert machine.get_state(0).position == old_pos


def test_move_state_merges_consecutive_moves(stack, machine):
    stack.push(MoveStateCommand(machine, 0, Point(0, 0), Point(10, 0)))
    stack.push(MoveStateCommand(machine, 0, Point(10, 0), Point(20, 0)))
    stack.push(MoveStateCommand(machine, 0, Point(20, 0), Point(30, 0)))
    assert stack.count() == 1  # merged into one
    stack.undo()
    assert machine.get_state(0).position == Point(0, 0)


def test_move_state_does_not_merge_different_states(stack, machine):
    stack.push(MoveStateCommand(machine, 0, Point(0, 0), Point(10, 0)))
    stack.push(MoveStateCommand(machine, 1, Point(100, 0), Point(110, 0)))
    assert stack.count() == 2


@pytest.mark.parametrize(
    "new_name, new_type, new_comment",
    [
        ("qX", StateType.NORMAL, "a comment"),
        ("start", StateType.INITIAL, ""),
        ("end", StateType.FINAL, "final state"),
    ],
)
def test_edit_state_redo(stack, machine, new_name, new_type, new_comment):
    stack.push(EditStateCommand(machine, 1, new_name, new_type, new_comment))
    state = machine.get_state(1)
    assert state.name == new_name
    assert state.state_type == new_type
    assert state.comment == new_comment


def test_edit_state_undo(stack, machine):
    state = machine.get_state(1)
    original_name = state.name
    original_type = state.state_type
    stack.push(EditStateCommand(machine, 1, "new_name", StateType.FINAL, ""))
    stack.undo()
    assert state.name == original_name
    assert state.state_type == original_type


def test_add_transition_redo(stack, machine):
    transition = Transition(from_state=1, to_state=2, functions=[TransitionFunction("b", "B", Direction.LEFT)])
    stack.push(AddTransitionCommand(machine, transition))
    assert transition in machine.transitions


def test_add_transition_undo(stack, machine):
    transition = Transition(from_state=1, to_state=2, functions=[TransitionFunction("b", "B", Direction.LEFT)])
    stack.push(AddTransitionCommand(machine, transition))
    stack.undo()
    assert transition not in machine.transitions


def test_remove_transition_redo(stack, machine):
    transition = machine.transitions[0]
    stack.push(RemoveTransitionCommand(machine, transition))
    assert transition not in machine.transitions


def test_remove_transition_undo(stack, machine):
    transition = machine.transitions[0]
    stack.push(RemoveTransitionCommand(machine, transition))
    stack.undo()
    assert transition in machine.transitions


@pytest.mark.parametrize(
    "new_functions",
    [
        [TransitionFunction("x", "X", Direction.LEFT)],
        [TransitionFunction("a", "A", Direction.RIGHT), TransitionFunction("b", "B", Direction.LEFT)],
    ],
)
def test_edit_transition_redo(stack, machine, new_functions):
    transition = machine.transitions[0]
    stack.push(EditTransitionCommand(transition, new_functions))
    assert transition.functions == new_functions


def test_edit_transition_undo(stack, machine):
    transition = machine.transitions[0]
    original = list(transition.functions)
    new = [TransitionFunction("x", "X", Direction.LEFT)]
    stack.push(EditTransitionCommand(transition, new))
    stack.undo()
    assert transition.functions == original


@pytest.mark.parametrize("new_point", [Point(50, 25), Point(-10, 100)])
def test_move_control_point_redo(stack, machine, new_point):
    transition = machine.transitions[0]
    stack.push(MoveControlPointCommand(transition, transition.control_point, new_point))
    assert transition.control_point == new_point


def test_move_control_point_undo(stack, machine):
    transition = machine.transitions[0]
    old = transition.control_point
    stack.push(MoveControlPointCommand(transition, old, Point(99, 99)))
    stack.undo()
    assert transition.control_point == old


def test_move_control_point_merges_consecutive(stack, machine):
    transition = machine.transitions[0]
    stack.push(MoveControlPointCommand(transition, Point(0, 0), Point(10, 0)))
    stack.push(MoveControlPointCommand(transition, Point(10, 0), Point(20, 0)))
    stack.push(MoveControlPointCommand(transition, Point(20, 0), Point(30, 0)))
    assert stack.count() == 1
    stack.undo()
    assert transition.control_point == Point(0, 0)


def test_full_undo_redo_sequence(stack, machine):
    """Add a state, edit it, undo both, redo both."""
    state = State(id=3, name="q3", state_type=StateType.NORMAL)
    stack.push(AddStateCommand(machine, state))
    stack.push(EditStateCommand(machine, 3, "qNew", StateType.FINAL, "edited"))

    assert machine.get_state(3).name == "qNew"

    stack.undo()
    assert machine.get_state(3).name == "q3"

    stack.undo()
    assert machine.get_state(3) is None

    stack.redo()
    assert machine.get_state(3) is not None

    stack.redo()
    assert machine.get_state(3).name == "qNew"
