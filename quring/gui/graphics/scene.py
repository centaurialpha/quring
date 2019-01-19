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

import enum

from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QPen
from PySide2.QtCore import QRectF
from PySide2.QtCore import QPointF
from PySide2.QtCore import Qt


class ItemMode(enum.IntEnum):
    INSERT = 0
    SELECT = 1


class Scene(QGraphicsScene):

    def __init__(self, automata_view):
        super().__init__()
        self._view = automata_view
        self.setSceneRect(QRectF(-5000, -5000, 5000, 5000))
        self._mode = ItemMode.SELECT
        self._ctrl_pressed = False

    def mousePressEvent(self, event):
        if self._mode == ItemMode.INSERT:
            item = StateItem(self._view)
            item.setPos(
                event.scenePos() - QPointF(item.boundingRect().width() / 2, item.boundingRect().height() / 2))
            self.addItem(item)
        elif self._mode == ItemMode.SELECT:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self._mode = ItemMode.INSERT

    def keyReleaseEvent(self, event):
        if self._mode == ItemMode.INSERT:
            self._mode = ItemMode.SELECT

    def mouseMoveEvent(self, event):
        # if self._mode == ItemMode.SELECT:
        super().mouseMoveEvent(event)


_GLOBAL_STATE_NUMBER = -1


class StateItem(QGraphicsItem):

    def __init__(self, view):
        super().__init__()
        global _GLOBAL_STATE_NUMBER
        _GLOBAL_STATE_NUMBER = _GLOBAL_STATE_NUMBER + 1
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setZValue(0)
        self.setAcceptHoverEvents(True)
        self._view = view
        self._hover = False

    def boundingRect(self):
        return QRectF(0, 0, 30 * 2, 30 * 2)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.black, 1)
        if self._hover:
            pen.setColor(Qt.blue)
        if self.isSelected():
            pen.setColor(Qt.red)
            pen.setWidth(2)

        painter.setPen(pen)
        painter.drawEllipse(self.boundingRect())

        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(_GLOBAL_STATE_NUMBER))

    def hoverEnterEvent(self, event):
        self._hover = True
        self.update(self.boundingRect())

    def hoverLeaveEvent(self, event):
        self._hover = False
        self.update(self.boundingRect())