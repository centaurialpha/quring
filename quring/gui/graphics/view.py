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

from PySide2.QtWidgets import QGraphicsView
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence


class AutomataView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

    # def wheelEvent(self, event):
    #     if event.modifiers() == Qt.ControlModifier:
    #         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    #         factor = 1.15
    #         if event.delta() > 0:
    #             self.scale(factor, factor)
    #         else:
    #             self.scale(1.0 / factor, 1.0 / factor)
    #     else:
    #         super().wheelEvent(event)