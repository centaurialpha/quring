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

from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPainterPath
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QPolygon
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen
from PySide2.QtGui import QFont
from PySide2.QtCore import QPoint
from PySide2.QtCore import QRect
from PySide2.QtCore import Qt
from PySide2.QtCore import QSize


class _Cinta:

    def __init__(self):
        self._memory = {}

    def read(self, position: int) -> str:
        try:
            return self._memory[position]
        except KeyError:
            return "#"

    def write(self, position: int, value: str):
        self._memory[position] = value

    def clear(self):
        self._memory.clear()

    def set_word(self, position: int, word: str):
        pos = position
        for char in word:
            self.write(pos, char)
            pos += 1


class Cinta(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self._font = QFont('Monospaced')
        self._font.setStyleHint(QFont.TypeWriter)
        self._font.setPointSize(11)
        self._tape = _Cinta()
        self._tape.set_word(0, 'MECHIII')

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        return QSize(0, 40)

    def set_palabra(self, palabra: str):
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self._font)
        painter.fillRect(event.rect(), QColor(Qt.white))
        fm = QFontMetrics(self._font)
        char_width = fm.width(' ')
        char_height = fm.height()
        cw = fm.width(' ') + 15
        ch = fm.height() + 5
        # margin = 10
        # Dibujo la cinta
        tape_color = QColor(Qt.gray).light(130)
        rect = QRect(0, 3, self.width(), self.height() - 6)
        painter.fillRect(rect, tape_color)
        # Dibujo el borde
        border_rect = QRect(rect)
        painter.setPen(Qt.gray)
        painter.drawLine(border_rect.topLeft(), border_rect.topRight())
        painter.drawLine(border_rect.bottomLeft(), border_rect.bottomRight())

        center = QPoint(self.width() / 2, self.height() / 2)
        # Dibujo cuadraditos
        # tape_pos = 0
        x = center.x() + cw / 2
        while x > 0:
            x -= cw
            painter.drawLine(x, center.y() - ch / 2,
                             x, center.y() + ch / 2)
        # x = center.x() + char_width / 2
        # p = QPen(Qt.red, 4)
        # painter.setPen(p)
        # painter.drawPoint(QPoint(x, 10))

        # while x > 0:
        #     if tape_pos == 0:
        #         pass
        #     else:
        #         painter.drawLine(x, center.y() - ch / 4,
        #                          x, center.y() + ch / 2)
        #     painter.drawText((x - cw / 2) - fm.width(' ') / 2, center.y() + 5, self._tape.read(tape_pos))
        #     x -= cw
        #     tape_pos -= 1
        # x = center.x() - cw / 2
        # while x < self.width():
        #     painter.drawLine(x, center.y() - ch / 2,
        #                      x, center.y() + ch / 2)
        #     painter.drawText((x - cw / 2) - fm.width(' ') / 2, center.y() + 5, self._tape.read(tape_pos))
        #     x += cw
        #     tape_pos += 1

        # Dibujo el cabezal
        # pen = QPen(Qt.black, 2)
        # painter.setRenderHint(painter.Antialiasing)
        # painter.setPen(pen)
        # # pen.setCapStyle(Qt.RoundCap)
        # poly = QPolygon()
        # x = center.x() - 10
        # poly << QPoint(x, 1) << QPoint(x + 20, 1) << QPoint(x + 20, 7) << \
        #     QPoint(x + 10, 13) << QPoint(x, 7)
        # path = QPainterPath()
        # path.addPolygon(poly)
        # painter.fillPath(path, QColor("#2196F3"))
        # painter.drawPolygon(poly)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QVBoxLayout
    from PySide2.QtWidgets import QDialog
    app = QApplication([])
    d = QDialog()
    box = QVBoxLayout(d)
    box.setContentsMargins(0, 0, 0, 0)
    cinta = Cinta()
    box.addWidget(cinta)
    d.show()
    app.exec_()
