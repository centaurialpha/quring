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

from quring.controllers.command import AddStateCommand
from quring.controllers.document import Document, DocumentManager
from quring.model.state import State
from quring.model.types import StateType


def test_document_starts_clean(qapp):
    doc = Document()
    assert not doc.is_dirty


def test_document_becomes_dirty_after_command(qapp):
    doc = Document()
    doc.undo_stack.push(AddStateCommand(doc.machine, State(id=0, name="q0", state_type=StateType.INITIAL)))
    assert doc.is_dirty


def test_document_becomes_clean_after_save(qapp, tmp_path):
    doc = Document(name="test")
    doc.undo_stack.push(AddStateCommand(doc.machine, State(id=0, name="q0", state_type=StateType.INITIAL)))
    assert doc.is_dirty
    doc.save(tmp_path / "test.json")
    assert not doc.is_dirty


def test_document_undo_restores_clean(qapp):
    doc = Document()
    doc.undo_stack.push(AddStateCommand(doc.machine, State(id=0, name="q0", state_type=StateType.INITIAL)))
    doc.undo_stack.undo()
    assert not doc.is_dirty


@pytest.mark.parametrize(
    "name, is_dirty, expected_display",
    [
        ("my_machine", False, "my_machine"),
        ("my_machine", True, "my_machine*"),
        ("Untitled", False, "Untitled"),
        ("Untitled", True, "Untitled*"),
    ],
)
def test_display_name(qapp, name, is_dirty, expected_display):
    doc = Document(name=name)
    if is_dirty:
        doc.undo_stack.push(AddStateCommand(doc.machine, State(id=0, name="q0", state_type=StateType.INITIAL)))
    assert doc.display_name == expected_display


def test_save_without_path_raises(qapp):
    doc = Document()
    with pytest.raises(ValueError, match="path"):
        doc.save()


def test_save_as_updates_name_and_path(qapp, tmp_path):
    doc = Document()
    target = tmp_path / "renamed.json"
    doc.save_as(target)
    assert doc.path == target
    assert doc.name == "renamed"


def test_save_roundtrip_preserves_states(qapp, tmp_path):
    doc = Document(name="rt")
    doc.undo_stack.push(AddStateCommand(doc.machine, State(id=0, name="q0", state_type=StateType.INITIAL)))
    path = tmp_path / "rt.json"
    doc.save(path)

    manager = DocumentManager()
    loaded = manager.open_document(path)
    assert len(loaded.machine.states) == 1
    assert loaded.machine.get_state(0).name == "q0"


def test_manager_starts_empty(qapp):
    manager = DocumentManager()
    assert manager.is_empty
    assert manager.current is None


def test_new_document_becomes_current(qapp):
    manager = DocumentManager()
    doc = manager.new_document()
    assert manager.current is doc


@pytest.mark.parametrize("count", [1, 2, 5])
def test_manager_tracks_all_documents(qapp, count):
    manager = DocumentManager()
    docs = [manager.new_document(f"doc{i}") for i in range(count)]
    assert len(manager.documents) == count
    for doc in docs:
        assert doc in manager.documents


def test_open_same_file_twice_returns_same_document(qapp, tmp_path):
    manager = DocumentManager()
    doc1 = manager.new_document("x")
    doc1.save(tmp_path / "x.json")

    opened1 = manager.open_document(tmp_path / "x.json")
    opened2 = manager.open_document(tmp_path / "x.json")
    assert opened1 is opened2


def test_close_document_removes_it(qapp):
    manager = DocumentManager()
    doc = manager.new_document()
    manager.close_document(doc)
    assert doc not in manager.documents
    assert manager.is_empty


def test_close_last_document_leaves_no_current(qapp):
    manager = DocumentManager()
    doc = manager.new_document()
    manager.close_document(doc)
    assert manager.current is None


def test_close_middle_document_keeps_valid_current(qapp):
    manager = DocumentManager()
    d0 = manager.new_document("d0")
    d1 = manager.new_document("d1")
    d2 = manager.new_document("d2")
    manager.close_document(d1)
    assert manager.current in (d0, d2)


def test_set_current(qapp):
    manager = DocumentManager()
    d0 = manager.new_document("d0")
    d1 = manager.new_document("d1")
    manager.set_current(d0)
    assert manager.current is d0
