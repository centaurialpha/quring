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

import json
from pathlib import Path
from typing import Any

from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import Transition, TransitionFunction
from quring.model.types import Direction, Point, StateType

# Bump this when the format changes in a breaking way.
FORMAT_VERSION = 1


def _encode_state(state: State) -> dict[str, Any]:
    return {
        "id": state.id,
        "name": state.name,
        "type": state.state_type.name.lower(),
        "x": state.position.x,
        "y": state.position.y,
        "comment": state.comment,
    }


def _encode_transition(transition: Transition) -> dict[str, Any]:
    return {
        "from": transition.from_state,
        "to": transition.to_state,
        "control_x": transition.control_point.x,
        "control_y": transition.control_point.y,
        "functions": [
            {
                "read": function.read,
                "write": function.write,
                "move": function.move.name.lower(),
            }
            for function in transition.functions
        ],
    }


def _decode_state(data: dict[str, Any]) -> State:
    states = {state_type.name.lower(): state_type for state_type in StateType}

    return State(
        id=data["id"],
        name=data["name"],
        state_type=states[data["type"]],
        position=Point(data.get("x", 0.0), data.get("y", 0.0)),
        comment=data.get("comment", ""),
    )


def _decode_transition(data: dict[str, Any]) -> Transition:
    direction = {direction.name.lower(): direction for direction in Direction}

    return Transition(
        from_state=data["from"],
        to_state=data["to"],
        control_point=Point(data.get("control_x", 0.0), data.get("control_y", 0.0)),
        functions=[
            TransitionFunction(
                read=function["read"],
                write=function["write"],
                move=direction[function["move"]],
            )
            for function in data.get("functions", [])
        ],
    )


class MachineSerializer:
    """
    Saves and loads TuringMachine instances as JSON.

    The format is self-contained and human-readable.  Canvas positions
    are preserved so the editor layout survives round-trips.

    Usage:
        MachineSerializer.save(machine, Path("my_machine.json"))
        machine = MachineSerializer.load(Path("my_machine.json"))
    """

    @staticmethod
    def save(machine: TuringMachine, path: Path | str, *, name: str = "", description: str = "") -> None:
        path = Path(path)
        payload: dict[str, Any] = {
            "version": FORMAT_VERSION,
            "meta": {
                "name": name,
                "description": description,
            },
            "states": [_encode_state(state) for state in machine.states],
            "transitions": [_encode_transition(transition) for transition in machine.transitions],
        }

        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    @staticmethod
    def load(path: Path | str) -> TuringMachine:
        path = Path(path)
        payload: dict[str, Any] = json.loads(path.read_text())

        version = payload.get("version", 1)
        if version > FORMAT_VERSION:
            raise ValueError(
                f"Files uses format version {version}, but this build only supports up to {FORMAT_VERSION}"
            )

        machine = TuringMachine()

        for state_data in payload.get("states", []):
            machine.add_state(_decode_state(state_data))

        for transition_data in payload.get("transitions", []):
            machine.add_transition(_decode_transition(transition_data))

        return machine
