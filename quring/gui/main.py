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
import sys
import logging
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QApplication

logger = logging.getLogger('quring.main_window')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()


def start():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    logger.info('Showing main window')
    main_window.show()
    sys.exit(app.exec_())
