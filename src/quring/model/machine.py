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

from contextlib import suppress
from dataclasses import dataclass

from quring.model.state import State
from quring.model.tape import Tape
from quring.model.transition import Transition, TransitionFunction
from quring.model.types import Direction, MachineStatus


@dataclass
class StepResult:
    """Describes everything that happened during a single simulation step."""

    previous_state_id: int
    next_state_id: int
    tape_position: int
    symbol_read: str
    symbol_written: str
    status: MachineStatus
    direction: Direction | None = None


@dataclass
class ValidationError:
    message: str


class TuringMachine:
    """
    The core model. Holds states, transitions, a tape, and simulation state.

    This class has no Qt dependency — it can be instantiated and tested
    in plain Python.
    """

    def __init__(self) -> None:
        self._states: dict[int, State] = {}
        self._transitions: list[Transition] = []
        self._tape: Tape = Tape()
        self._current_state_id: int | None = None
        self._status: MachineStatus = MachineStatus.IDLE
        self._step_count: int = 0
        self._next_id: int = 0

    @property
    def states(self) -> list[State]:
        return list(self._states.values())

    @property
    def transitions(self) -> list[Transition]:
        return list(self._transitions)

    @property
    def tape(self) -> Tape:
        return self._tape

    @property
    def current_state_id(self) -> int | None:
        return self._current_state_id

    @property
    def status(self) -> MachineStatus:
        return self._status

    @property
    def step_count(self) -> int:
        return self._step_count

    def add_state(self, state: State) -> None:
        if state.id in self._states:
            raise ValueError(f"State with id={state.id} already exists.")
        self._states[state.id] = state
        self._next_id = max(self._next_id, state.id + 1)

    def remove_state(self, state_id: int) -> None:
        self._states.pop(state_id, None)
        # Remove all transitions that reference this state
        self._transitions = [
            transition
            for transition in self._transitions
            if transition.from_state != state_id and transition.to_state != state_id
        ]
        if self._current_state_id == state_id:
            self._current_state_id = None

    def get_state(self, state_id: int) -> State | None:
        return self._states.get(state_id)

    def get_initial_state(self) -> State | None:
        for state in self._states.values():
            if state.is_initial:
                return state
        return None

    def next_id(self) -> int:
        """Return a fresh unique ID and advance the internal counter."""
        id_ = self._next_id
        self._next_id += 1
        return id_

    def add_transition(self, transition: Transition) -> None:
        self._transitions.append(transition)

    def remove_transition(self, transition: Transition) -> None:
        with suppress(ValueError):
            self._transitions.remove(transition)

    def get_transitions_from(self, state_id: int) -> list[Transition]:
        return [transition for transition in self._transitions if transition.from_state == state_id]

    def reset(self) -> None:
        """
        Rewind simulation to the initial state without touching the tape.
        """
        initial = self.get_initial_state()
        self._current_state_id = initial.id if initial else None
        self._status = MachineStatus.IDLE
        self._step_count = 0

    def step(self) -> StepResult:
        """
        Execute one simulation step.

        Returns a StepResult describing what happened.
        Raises RuntimeError if the machine has no current state.
        """
        if self._current_state_id is None:
            raise RuntimeError("No active state - call reset() firts")

        previous_id = self._current_state_id
        current_state = self._states[previous_id]

        # If already in a final state, stay there.
        if current_state.is_final:
            self._status = MachineStatus.ACCEPTED
            return StepResult(
                previous_state_id=previous_id,
                next_state_id=previous_id,
                tape_position=self._tape.head_position,
                symbol_read=self._tape.read(),
                symbol_written=self._tape.read(),
                direction=None,
                status=MachineStatus.ACCEPTED,
            )

        symbol = self._tape.read()

        # Find the first matching transition.
        match: tuple[Transition, TransitionFunction] | None = None
        for transition in self.get_transitions_from(previous_id):
            func = transition.match(symbol)
            if func is not None:
                match = (transition, func)
                break

        if match is None:
            self._status = MachineStatus.JAMMED
            return StepResult(
                previous_state_id=previous_id,
                next_state_id=previous_id,
                tape_position=self._tape.head_position,
                symbol_read=symbol,
                symbol_written=symbol,
                direction=None,
                status=MachineStatus.JAMMED,
            )

        transition, fn = match

        # Apply the transition.
        self._tape.write(fn.write)
        if fn.move == Direction.LEFT:
            self._tape.move_left()
        else:
            self._tape.move_right()

        self._current_state_id = transition.to_state
        self._step_count += 1

        next_state = self._states.get(transition.to_state)
        if next_state and next_state.is_final:
            self._status = MachineStatus.ACCEPTED
        else:
            self._status = MachineStatus.RUNNING

        return StepResult(
            previous_state_id=previous_id,
            next_state_id=transition.to_state,
            tape_position=self._tape.head_position,
            symbol_read=symbol,
            symbol_written=fn.write,
            direction=fn.move,
            status=self._status,
        )

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        initial_states = [state for state in self._states.values() if state.is_initial]
        if len(initial_states) == 0:
            errors.append(ValidationError("No initial state defined."))
        elif len(initial_states) > 1:
            errors.append(ValidationError(f"Multiple initial states: {[s.name for s in initial_states]}."))

        final_states = [state for state in self._states.values() if state.is_final]
        if len(final_states) == 0:
            errors.append(ValidationError("No final state defined."))

        for t in self._transitions:
            if t.from_state not in self._states:
                errors.append(ValidationError(f"Transition references unknown source state id={t.from_state}."))
            if t.to_state not in self._states:
                errors.append(ValidationError(f"Transition references unknown target state id={t.to_state}."))
            if not t.functions:
                errors.append(ValidationError(f"Transition {t.from_state}→{t.to_state} has no functions defined."))

        return errors

    def __repr__(self) -> str:
        return (
            f"TuringMachine("
            f"states={len(self._states)}, "
            f"transitions={len(self._transitions)}, "
            f"status={self._status.name})"
        )
