from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtGui import QPainter
from PySide2.QtGui import QColor
# from PySide2.QtGui import QFont
from PySide2.QtGui import QFontMetrics
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtCore import QRect
from PySide2.QtCore import QPoint
from PySide2.QtCore import QBasicTimer
# from PySide2.QtCore import QPointF


class Tape:

    def __init__(self, word: str):
        self._word = word

    def read(self, position: int) -> str:
        return self._word[position]

    def write(self, word: str, position: int):
        pass


class TapeWidget(QWidget):

    X_MARGIN = 0.0
    Y_MARGIN = 5.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self._timer = QBasicTimer()
        self._move = 0
        self._displace = 0
        self._seek_accel = 0
        self._header_pos = 0
        self._is_seeking = False
        self._speed = 1.0
        # self._font = QFont("monospaced")
        # self._font.setStyleHint(QFont.TypeWriter)
        # self._font.setPointSize(11)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: float):
        if value <= 0:
            raise
        self._speed = value

    def move_to(self, position: int):
        if self._header_pos == position and self._move == position:
            return
        self._move = position
        self._is_seeking = True
        self._seek_accel = abs(self._header_pos - position) * self._speed
        if not self._timer.isActive():
            self._timer.start(10, self)
        self.update()

    def move_right(self):
        self.move_to(self._move + 1)

    def move_left(self):
        self.move_to(self._move - 1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.move_left()
        elif event.key() == Qt.Key_Right:
            self.move_right()

    def timerEvent(self, event):
        if not self._is_seeking:
            self._timer.stop()
            return
        if self._move < self._header_pos:
            self._displace += self._seek_accel
            if abs(self._displace) >= 20:
                self._header_pos -= 1
                self._displace = 0
        else:
            self._displace -= self._seek_accel
            if abs(self._displace) >= 20:
                self._header_pos += 1
                self._displace = 0

        if self._header_pos == self._move:
            self._timer.stop()
            self._is_seeking = False
        self.update()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return QSize(0, 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.white)
        painter.setBrush(Qt.white)
        painter.drawRect(event.rect())
        painter.setPen(Qt.lightGray)
        r = QRect(event.rect()).adjusted(
            TapeWidget.X_MARGIN, TapeWidget.Y_MARGIN,
            -TapeWidget.X_MARGIN, -TapeWidget.Y_MARGIN
        )
        # Draw tape
        painter.fillRect(r, QColor(Qt.gray).light(150))
        painter.drawLine(r.topLeft(), r.topRight())
        painter.drawLine(r.bottomLeft(), r.bottomRight())

        fm = QFontMetrics(self.font())
        center = QPoint(self.width() / 2, self.height() / 2)

        cw = fm.width(' ') + 15
        # ch = fm.height() + 5

        x = self._displace + center.x() + cw / 2
        while x > 0:
            x -= cw
            painter.drawLine(x, r.y() + 5, x, r.bottom() - 5)

        x = self._displace + center.x() - cw / 2
        while x < self.width():
            x += cw
            painter.drawLine(x, r.y() + 5, x, r.bottom() - 5)

        # Draw head
        color = QColor('#00a8ff')
        color.setAlpha(100)
        painter.setBrush(color)
        painter.drawRect(center.x() - 15, 3, 29, 33)


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QDialog
    from PySide2.QtWidgets import QVBoxLayout
    app = QApplication([])
    dialog = QDialog()
    vbox = QVBoxLayout(dialog)
    w = TapeWidget()
    vbox.addWidget(w)
    dialog.show()
    app.exec_()
