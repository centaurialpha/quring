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


from pathlib import Path

from PySide6.QtGui import QUndoStack

from quring.model.machine import TuringMachine
from quring.serialization.serializer import MachineSerializer


class Document:
    """
    A single open Turing machine file.

    Bundles together:
    - The machine model
    - Its undo/redo stack
    - File metadata (path, dirty flag)

    The Document owns the QUndoStack. All edits must go through
    commands pushed onto this stack so that undo/redo works correctly.
    """

    def __init__(
        self,
        machine: TuringMachine | None = None,
        path: Path | None = None,
        name: str = "Untitled",
    ) -> None:
        self._machine = machine or TuringMachine()
        self._path = path
        self._name = name
        self._undo_stack = QUndoStack()
        self._undo_stack.cleanChanged.connect(self._on_clean_changed)

    @property
    def machine(self) -> TuringMachine:
        return self._machine

    @property
    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_dirty(self) -> bool:
        """True if there are unsaved changes."""
        return not self._undo_stack.isClean()

    @property
    def display_name(self) -> str:
        """Name shown in the tab — appends * when dirty."""
        return f"{self._name}{'*' if self.is_dirty else ''}"

    def save(self, path: Path | None = None) -> None:
        """
        Save to `path`, or to the document's current path if omitted.
        Raises ValueError if neither is set (use save_as instead).
        """
        target = path or self._path
        if target is None:
            raise ValueError("No path set — use save_as(path) for new documents.")
        MachineSerializer.save(self._machine, target, name=self._name)
        self._path = target
        self._undo_stack.setClean()

    def save_as(self, path: Path) -> None:
        self._name = path.stem
        self.save(path)

    def _on_clean_changed(self, clean: bool) -> None:
        # Hook for the view to update tab titles when dirty state changes.
        # The view connects to undo_stack.cleanChanged directly; this is
        # kept here for any document-level logic that may be needed later.
        pass


class DocumentManager:
    """
    Manages all open Documents (the multi-tab model).

    Keeps track of which document is active and provides open/close/save
    operations. Does not know about the UI — the view observes it.
    """

    def __init__(self) -> None:
        self._documents: list[Document] = []
        self._current_index: int = -1

    @property
    def documents(self) -> list[Document]:
        return list(self._documents)

    @property
    def current(self) -> Document | None:
        if 0 <= self._current_index < len(self._documents):
            return self._documents[self._current_index]
        return None

    @property
    def is_empty(self) -> bool:
        return len(self._documents) == 0

    def new_document(self, name: str = "Untitled") -> Document:
        doc = Document(name=name)
        self._add(doc)
        return doc

    def open_document(self, path: Path) -> Document:
        # If the file is already open, just switch to it.
        for i, doc in enumerate(self._documents):
            if doc.path == path:
                self._current_index = i
                return doc

        machine = MachineSerializer.load(path)
        doc = Document(machine=machine, path=path, name=path.stem)
        self._add(doc)
        return doc

    def close_document(self, doc: Document) -> None:
        if doc not in self._documents:
            return
        idx = self._documents.index(doc)
        self._documents.remove(doc)
        # Keep current_index valid.
        if not self._documents:
            self._current_index = -1
        else:
            self._current_index = min(idx, len(self._documents) - 1)

    def set_current(self, doc: Document) -> None:
        if doc in self._documents:
            self._current_index = self._documents.index(doc)

    def _add(self, doc: Document) -> None:
        self._documents.append(doc)
        self._current_index = len(self._documents) - 1
