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

import pytest

from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import Transition, TransitionFunction
from quring.model.types import Direction, Point, StateType
from quring.serialization.serializer import MachineSerializer


@pytest.fixture
def tmp_json(tmp_path: Path) -> Path:
    return tmp_path / "machine.json"


@pytest.fixture
def simple_machine() -> TuringMachine:
    """q0 --(a/A, R)--> q1 --(b/B, L)--> q2 (final)"""
    machine = TuringMachine()
    machine.add_state(State(id=0, name="q0", state_type=StateType.INITIAL, position=Point(10.0, 20.0), comment="start"))
    machine.add_state(State(id=1, name="q1", state_type=StateType.NORMAL, position=Point(50.0, 0.0)))
    machine.add_state(State(id=2, name="q2", state_type=StateType.FINAL, position=Point(90.0, 20.0)))
    machine.add_transition(
        Transition(
            from_state=0,
            to_state=1,
            control_point=Point(30.0, 5.0),
            functions=[TransitionFunction(read="a", write="A", move=Direction.RIGHT)],
        )
    )
    machine.add_transition(
        Transition(
            from_state=1,
            to_state=2,
            functions=[
                TransitionFunction(read="b", write="B", move=Direction.LEFT),
                TransitionFunction(read="c", write="C", move=Direction.LEFT),
            ],
        )
    )
    return machine


def test_roundtrip_state_count(simple_machine, tmp_json):
    MachineSerializer.save(simple_machine, tmp_json)
    loaded = MachineSerializer.load(tmp_json)
    assert len(loaded.states) == len(simple_machine.states)


def test_empty_machine_roundtrip(tmp_json):
    machine = TuringMachine()
    MachineSerializer.save(machine, tmp_json)
    loaded = MachineSerializer.load(tmp_json)
    assert loaded.states == []
    assert loaded.transitions == []


def test_roundtrip_transition_count(simple_machine, tmp_json):
    MachineSerializer.save(simple_machine, tmp_json)
    loaded = MachineSerializer.load(tmp_json)
    assert len(loaded.transitions) == len(simple_machine.transitions)


@pytest.mark.parametrize(
    "state_id, name, state_type, position, comment",
    [
        (0, "q0", StateType.INITIAL, Point(10.0, 20.0), "start"),
        (1, "q1", StateType.NORMAL, Point(50.0, 0.0), ""),
        (2, "q2", StateType.FINAL, Point(90.0, 20.0), ""),
    ],
)
def test_roundtrip_state_fields(simple_machine, tmp_json, state_id, name, state_type, position, comment):
    MachineSerializer.save(simple_machine, tmp_json)
    loaded = MachineSerializer.load(tmp_json)
    state = loaded.get_state(state_id)
    assert state is not None
    assert state.name == name
    assert state.state_type == state_type
    assert state.position == position
    assert state.comment == comment


@pytest.mark.parametrize(
    "from_state, to_state, control_point, expected_functions",
    [
        (
            0,
            1,
            Point(30.0, 5.0),
            [TransitionFunction("a", "A", Direction.RIGHT)],
        ),
        (
            1,
            2,
            Point(0.0, 0.0),
            [
                TransitionFunction("b", "B", Direction.LEFT),
                TransitionFunction("c", "C", Direction.LEFT),
            ],
        ),
    ],
)
def test_roundtrip_transition_fields(simple_machine, tmp_json, from_state, to_state, control_point, expected_functions):
    MachineSerializer.save(simple_machine, tmp_json)
    loaded = MachineSerializer.load(tmp_json)
    matches = [t for t in loaded.transitions if t.from_state == from_state and t.to_state == to_state]
    assert len(matches) == 1
    t = matches[0]
    assert t.control_point == control_point
    assert t.functions == expected_functions


def test_saved_file_is_valid_json(simple_machine, tmp_json):
    MachineSerializer.save(simple_machine, tmp_json)
    payload = json.loads(tmp_json.read_text())
    assert isinstance(payload, dict)


def test_saved_file_contains_version(simple_machine, tmp_json):
    MachineSerializer.save(simple_machine, tmp_json)
    payload = json.loads(tmp_json.read_text())
    assert "version" in payload


@pytest.mark.parametrize(
    "meta_key, meta_value",
    [
        ("name", "My Machine"),
        ("description", "A test machine"),
    ],
)
def test_save_includes_meta(simple_machine, tmp_json, meta_key, meta_value):
    MachineSerializer.save(simple_machine, tmp_json, name="My Machine", description="A test machine")
    payload = json.loads(tmp_json.read_text())
    assert payload["meta"][meta_key] == meta_value


@pytest.mark.parametrize(
    "direction, expected_str",
    [
        (Direction.RIGHT, "right"),
        (Direction.LEFT, "left"),
    ],
)
def test_direction_serialized_as_lowercase_string(tmp_json, direction, expected_str):
    m = TuringMachine()
    m.add_state(State(id=0, name="q0", state_type=StateType.INITIAL))
    m.add_state(State(id=1, name="q1", state_type=StateType.FINAL))
    m.add_transition(
        Transition(
            from_state=0,
            to_state=1,
            functions=[TransitionFunction("a", "a", direction)],
        )
    )
    MachineSerializer.save(m, tmp_json)
    payload = json.loads(tmp_json.read_text())
    assert payload["transitions"][0]["functions"][0]["move"] == expected_str


@pytest.mark.parametrize(
    "state_type, expected_str",
    [
        (StateType.INITIAL, "initial"),
        (StateType.NORMAL, "normal"),
        (StateType.FINAL, "final"),
    ],
)
def test_state_type_serialized_as_lowercase_string(tmp_json, state_type, expected_str):
    m = TuringMachine()
    m.add_state(State(id=0, name="q", state_type=state_type))
    MachineSerializer.save(m, tmp_json)
    payload = json.loads(tmp_json.read_text())
    assert payload["states"][0]["type"] == expected_str


def test_load_nonexistent_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        MachineSerializer.load(tmp_path / "ghost.json")


def test_load_invalid_json_raises(tmp_json):
    tmp_json.write_text("this is not json {{{")
    with pytest.raises(Exception):
        MachineSerializer.load(tmp_json)


def test_load_future_version_raises(tmp_json):
    tmp_json.write_text(json.dumps({"version": 9999, "states": [], "transitions": []}))
    with pytest.raises(ValueError, match="version"):
        MachineSerializer.load(tmp_json)
