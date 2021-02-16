import sys

import cv2

import numpy as np
import pyrealsense2 as rs

rs.__path__
['/usr/lib/python3/dist-packages/pyrealsense2']


# OnScreen Keyboard

# Keyboard Section
class InputState: 
    LOWER = 0
    CAPITAL = 1

class KeyButton(QPushButton):
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(50,50)
        self.clicked.connect(self.emitKey)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def emitKey(self):
        self.sigKeyButtonClicked.emit()

    def enterEvent(self, event):
        self.setFixedSize(self._activeSize)

    def leaveEvent(self, event):
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(40, 40)
