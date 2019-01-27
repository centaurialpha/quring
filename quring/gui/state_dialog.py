# -*- coding: utf-8 -*-
#
# Copyright 2019 - Gabriel Acosta <acostadariogabriel@gmail.com>
#
# This file is part of Quring.
#
# Quring is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Quring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Quring; If not, see <http://www.gnu.org/licenses/>.

from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QLabel

from quring.gui.graphics.scene import StateType


class StateDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('State Editor')
        vbox = QVBoxLayout(self)
        layout = QGridLayout()
        self._line_name = QLineEdit()
        layout.addWidget(QLabel('Name'), 0, 0)
        layout.addWidget(self._line_name, 0, 1)

        self._combo_state_type = QComboBox()
        self._combo_state_type.addItems(["Normal", "Final", "Initial"])
        layout.addWidget(QLabel('Type'), 1, 0)
        layout.addWidget(self._combo_state_type, 1, 1)
        vbox.addLayout(layout)
        vbox.addWidget(QLabel('Comment'))

        self._comment = QTextEdit()
        vbox.addWidget(self._comment)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        btn_save = QPushButton('Save')
        hbox.addWidget(btn_save)
        btn_cancel = QPushButton('Cancel')
        hbox.addWidget(btn_cancel)
        vbox.addLayout(hbox)

        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def get_name(self):
        return self._line_name.text().strip()

    def get_comment(self):
        return self._comment.toPlainText().strip()

    def get_state_type(self):
        states_map = {
            0: StateType.NORMAL,
            1: StateType.FINAL,
            2: StateType.INITIAL
        }
        return states_map.get(self._combo_state_type.currentIndex())
