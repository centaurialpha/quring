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
from PySide2.QtCore import QSettings

from quring.core import paths
from quring.gui import central

logger = logging.getLogger('quring.main_window')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(750, 500)
        self._load_geometry()
        self.setWindowTitle('Quring - Turing Machine Simulator')

        self.central = central.CentralWidget(self)
        self.setCentralWidget(self.central)

    def _load_geometry(self):
        qsettings = QSettings(paths.SETTINGS, QSettings.IniFormat)
        is_fullscreen = qsettings.value('window/fullscren', False)
        if is_fullscreen:
            self.showFullScreen()
        else:
            size = qsettings.value('window/size')
            position = qsettings.value('window/position')
            if size is not None:
                self.resize(size)
            if position is not None:
                self.move(position)

    def closeEvent(self, event):
        """Save some settings before close"""
        qsettings = QSettings(paths.SETTINGS, QSettings.IniFormat)
        qsettings.setValue('window/size', self.size())
        qsettings.setValue('window/fullscreen', self.isFullScreen())
        qsettings.setValue('window/position', self.pos())

        super().closeEvent(event)


def start():
    app = QApplication(sys.argv)
    app.setOrganizationName('Quring')
    app.setOrganizationDomain('Quring')
    app.setApplicationName('Quring')

    main_window = MainWindow()
    logger.info('Showing main window')
    main_window.show()
    sys.exit(app.exec_())
