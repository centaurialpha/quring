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

"""
scratch.py — Quring interactive playground

Usage inside IPython:
    %run scratch.py

    available()
    run("anbn", "aabb")
    step_through("increment", "101")
    m = run("copy", "aaa")
    m.tape.as_string()
"""

from quring.model.machine import TuringMachine
from quring.model.state import State
from quring.model.transition import BLANK, Transition, TransitionFunction
from quring.model.types import Direction, StateType


def build(states: list[tuple], transitions: list[tuple]) -> TuringMachine:
    machine = TuringMachine()
    for sid, name, stype in states:
        machine.add_state(State(id=sid, name=name, state_type=stype))
    for frm, to, fns in transitions:
        machine.add_transition(
            Transition(
                from_state=frm,
                to_state=to,
                functions=[TransitionFunction(r, w, d) for r, w, d in fns],
            )
        )
    return machine


def make_anb() -> TuringMachine:
    return build(
        states=[
            (0, "q1", StateType.INITIAL),
            (1, "q2", StateType.FINAL),
        ],
        transitions=[
            (0, 0, [("a", "a", Direction.RIGHT)]),
            (0, 1, [("b", "b", Direction.RIGHT)]),
        ],
    )


def make_anbn() -> TuringMachine:
    return build(
        states=[
            (0, "q0", StateType.INITIAL),
            (1, "q1", StateType.NORMAL),
            (2, "q2", StateType.NORMAL),
            (3, "q3", StateType.NORMAL),
            (4, "q4", StateType.FINAL),
        ],
        transitions=[
            (0, 1, [("a", "X", Direction.RIGHT)]),
            (0, 3, [("Y", "Y", Direction.RIGHT)]),
            (1, 1, [("a", "a", Direction.RIGHT), ("X", "X", Direction.RIGHT), ("Y", "Y", Direction.RIGHT)]),
            (1, 2, [("b", "Y", Direction.LEFT)]),
            (2, 2, [("a", "a", Direction.LEFT), ("Y", "Y", Direction.LEFT)]),
            (2, 0, [("X", "X", Direction.RIGHT)]),
            (3, 3, [("Y", "Y", Direction.RIGHT)]),
            (3, 4, [(BLANK, BLANK, Direction.RIGHT)]),
        ],
    )


def make_binary_invert():
    return build(
        states=[
            (0, "q0", StateType.INITIAL),
            (1, "q1", StateType.FINAL),
        ],
        transitions=[
            (0, 0, [("1", "0", Direction.RIGHT)]),
            (0, 0, [("0", "1", Direction.RIGHT)]),
            (0, 1, [("#", "#", Direction.RIGHT)]),
        ],
    )


MACHINES: dict[str, tuple[callable, str]] = {
    "binary_invert": (make_binary_invert, ""),
    "anb": (make_anb, "Accepts a^nb"),
    "anbn": (make_anbn, "Accepts a^n b^n - 'aabb', 'aaabb'"),
}


def available() -> None:
    """Print available machine names and descriptions."""
    print("Available machines:")
    for name, (_, description) in MACHINES.items():
        print(f"  {name:<12s} {description}")


def _setup(machine_name: str, input_str: str) -> TuringMachine | None:
    entry = MACHINES.get(machine_name)
    if entry is None:
        print(f"Unknown machine {machine_name!r}")
        return None

    factory, _ = entry
    machine = factory()
    errors = machine.validate()
    if errors:
        for error in errors:
            print(f"{error.message}")
        return None

    machine.tape.set_content(input_str)
    machine.reset()
    return machine


def show_tape(machine: TuringMachine, padding: int = 3) -> None:
    assert isinstance(machine.current_state_id, int)
    state = machine.get_state(machine.current_state_id)
    name = state.name if state else "-"
    print(f"state={name:<10s} steps={machine.step_count:>3d} {machine.tape.as_string(padding)}")


def run(machine_name: str, input_str: str, max_steps: int = 500) -> TuringMachine | None:
    machine = _setup(machine_name, input_str)
    if machine is None:
        return None

    print("-" * 20)
    print(f"    machine: {machine_name}")
    print(f"    input: {input_str}")
    print("-" * 20)
    show_tape(machine)

    while not machine.status.is_terminal and machine.step_count < max_steps:
        machine.step()

    if machine.step_count >= max_steps:
        print("Stopped")

    show_tape(machine)
    print("-" * 20)
    return machine


def show_step(result) -> None:
    arrow = {Direction.LEFT: "L", Direction.RIGHT: "R"}[result.direction]
    print(
        f"q{result.previous_state_id} -> q{result.next_state_id} "
        f"read={result.symbol_read!r} write={result.symbol_written!r} {arrow}"
    )


def step_through(machine_name: str, input_str: str, max_steps: int = 100) -> TuringMachine | None:
    """
    Run a machine one step at a time, printing each transition.

    Examples:
        step_through("anbn", "ab")
        step_through("increment", "101")
        step_through("copy", "aa")
    """

    machine = _setup(machine_name, input_str)
    assert machine is not None

    show_tape(machine)

    while not machine.status.is_terminal and machine.step_count < max_steps:
        result = machine.step()
        show_step(result)
        # show_tape(machine)

    if machine.step_count >= max_steps:
        print("Stop")

    return machine


if __name__ == "__main__":
    # available()
    # print(_setup("anbn", "aaaaabbbb"))
    # run("anbn", "abbbbbbbbbbbb")
    # print(run("anb", "aaaaaaaa"))
    # print(run("binary_invert", "1001"))
    step_through("anb", "aab")
