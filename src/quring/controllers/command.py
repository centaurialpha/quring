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

from PySide6.QtGui import QUndoCommand

from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import Transition, TransitionFunction
from quring.model.types import Point, StateType


# Qt requires id() to return a positive int32.
# Truncate Python memory address to 31 bits — sufficient for a UI editor.
def _transition_id(t: Transition) -> int:
    return id(t) & 0x7FFF_FFFF


class AddStateCommand(QUndoCommand):
    def __init__(self, machine: TuringMachine, state: State) -> None:
        super().__init__(f"Add state '{state.name}'")
        self._machine = machine
        self._state = state

    def redo(self) -> None:
        self._machine.add_state(self._state)

    def undo(self) -> None:
        self._machine.remove_state(self._state.id)


class RemoveStateCommand(QUndoCommand):
    def __init__(self, machine: TuringMachine, state_id: int) -> None:
        state = machine.get_state(state_id)
        super().__init__(f"Remove state '{state.name if state else state_id}'")
        self._machine = machine
        self._state_id = state_id
        self._state = state
        self._affected_transitions = [
            transition
            for transition in machine.transitions
            if transition.from_state == state_id or transition.to_state == state_id
        ]

    def redo(self) -> None:
        self._machine.remove_state(self._state_id)

    def undo(self) -> None:
        if self._state:
            self._machine.add_state(self._state)
        for transition in self._affected_transitions:
            self._machine.add_transition(transition)


class MoveStateCommand(QUndoCommand):
    def __init__(self, machine: TuringMachine, state_id: int, old_pos: Point, new_pos: Point) -> None:
        super().__init__("Move state")
        self._machine = machine
        self._state_id = state_id
        self._old_pos = old_pos
        self._new_pos = new_pos

    def id(self) -> int:
        return self._state_id

    def redo(self) -> None:
        self._apply(self._new_pos)

    def undo(self) -> None:
        self._apply(self._old_pos)

    def mergeWith(self, other: QUndoCommand, /) -> bool:
        if not isinstance(other, MoveStateCommand):
            return False
        if other._state_id != self._state_id:
            return False
        self._new_pos = other._new_pos
        return True

    def _apply(self, pos: Point) -> None:
        state = self._machine.get_state(self._state_id)
        if state:
            state.position = pos


class EditStateCommand(QUndoCommand):
    def __init__(
        self,
        machine: TuringMachine,
        state_id: int,
        new_name: str,
        new_type: StateType,
        new_comment: str,
    ) -> None:
        super().__init__("Edit state")
        self._machine = machine
        self._state_id = state_id
        state = machine.get_state(state_id)
        self._old_name = state.name if state else ""
        self._old_type = state.state_type if state else StateType.NORMAL
        self._old_comment = state.comment if state else ""
        self._new_name = new_name
        self._new_type = new_type
        self._new_comment = new_comment

    def redo(self) -> None:
        self._apply(self._new_name, self._new_type, self._new_comment)

    def undo(self) -> None:
        self._apply(self._old_name, self._old_type, self._old_comment)

    def _apply(self, name: str, state_type: StateType, comment: str) -> None:
        state = self._machine.get_state(self._state_id)
        if state:
            state.name = name
            state.state_type = state_type
            state.comment = comment


class AddTransitionCommand(QUndoCommand):
    def __init__(self, machine: TuringMachine, transition: Transition) -> None:
        super().__init__(f"Add transition {transition.from_state} → {transition.to_state}")
        self._machine = machine
        self._transition = transition

    def redo(self) -> None:
        self._machine.add_transition(self._transition)

    def undo(self) -> None:
        self._machine.remove_transition(self._transition)


class RemoveTransitionCommand(QUndoCommand):
    def __init__(self, machine: TuringMachine, transition: Transition) -> None:
        super().__init__(f"Remove transition {transition.from_state} → {transition.to_state}")
        self._machine = machine
        self._transition = transition

    def redo(self) -> None:
        self._machine.remove_transition(self._transition)

    def undo(self) -> None:
        self._machine.add_transition(self._transition)


class EditTransitionCommand(QUndoCommand):
    def __init__(
        self,
        transition: Transition,
        new_functions: list[TransitionFunction],
    ) -> None:
        super().__init__(f"Edit transition {transition.from_state} → {transition.to_state}")
        self._transition = transition
        self._old_functions = list(transition.functions)
        self._new_functions = list(new_functions)

    def redo(self) -> None:
        self._transition.functions = list(self._new_functions)

    def undo(self) -> None:
        self._transition.functions = list(self._old_functions)


class MoveControlPointCommand(QUndoCommand):
    def __init__(
        self,
        transition: Transition,
        old_point: Point,
        new_point: Point,
    ) -> None:
        super().__init__("Move control point")
        self._transition = transition
        self._old_point = old_point
        self._new_point = new_point

    def id(self) -> int:
        return _transition_id(self._transition)

    def redo(self) -> None:
        self._transition.control_point = self._new_point

    def undo(self) -> None:
        self._transition.control_point = self._old_point

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, MoveControlPointCommand):
            return False
        if other._transition is not self._transition:
            return False
        self._new_point = other._new_point
        return True
