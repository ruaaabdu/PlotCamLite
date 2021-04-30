"""
This code handles the virtual keyboard functions
@author Ruaa Abdulmajeed
@date April 30th, 2021
"""
# PyQt Widgets for the applicaton and layout
from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QSizePolicy, QVBoxLayout, QWidget)
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont

from util import DEFAULT_FONT

class InputState:
    LOWER = 0
    CAPITAL = 1

class KeyButton(QPushButton):
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(90, 90)
        self.clicked.connect(self.emitKey)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def emitKey(self):
        self.sigKeyButtonClicked.emit()

    def enterEvent(self, event):
        self.setFixedSize(self._activeSize)

    def leaveEvent(self, event):
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(90, 90)

class VirtualKeyboard(QWidget):
    sigInputString = pyqtSignal()
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self):
        super(VirtualKeyboard, self).__init__()

        self.globalLayout = QVBoxLayout(self)
        self.keysLayout = QGridLayout()
        self.buttonLayout = QHBoxLayout()

        self.keyListByLines = [
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["Z", "X", "C", "V", "B", "N", "_", ".", "/", " "],
        ]
        self.inputString = "" ## resetting input
        self.state = InputState.CAPITAL

        self.backButton = QPushButton()
        self.backButton.setText("DELETE")
        self.cancelButton = QPushButton()
        self.cancelButton.setText("CANCEL")

        self.currentLineEdit = QLineEdit()

        for lineIndex, line in enumerate(self.keyListByLines):
            for keyIndex, key in enumerate(line):
                buttonName = "keyButton" + key.capitalize()
                
                self.__setattr__(buttonName, KeyButton(key))
                self.keysLayout.addWidget(
                    self.getButtonByKey(key),
                    self.keyListByLines.index(line),
                    line.index(key),
                )

                
                self.getButtonByKey(key).setText(key)
                self.getButtonByKey(key).setFont(DEFAULT_FONT)
                self.getButtonByKey(key).sigKeyButtonClicked.connect(
                    lambda v=key: self.addInputByKey(v)
                )

                self.keysLayout.setColumnMinimumWidth(keyIndex, 50)
                
            self.keysLayout.setRowMinimumHeight(lineIndex, 50)

        self.backButton.clicked.connect(self.backspace)
        self.cancelButton.clicked.connect(self.emitCancel)

        self.backButton.setFont(DEFAULT_FONT)
        self.cancelButton.setFont(DEFAULT_FONT)

        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.backButton)

        self.globalLayout.addLayout(self.keysLayout)

        self.globalLayout.addLayout(self.buttonLayout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    def getButtonByKey(self, key):
        return getattr(self, "keyButton" + key.capitalize())

    def getLineForButtonByKey(self, key):
        return [key in keyList for keyList in self.keyListByLines].index(True)

    @pyqtSlot(QLineEdit)
    def setLineEdit(self, line_edit):
        # deadling with old line edit
        if self.currentLineEdit == line_edit: #clicked the same line edit they were on
            return

        # updating new line edit
        self.currentLineEdit = line_edit 

        self.inputString = self.currentLineEdit.text()

    def addInputByKey(self, key):
        self.inputString += (key.lower(), key.capitalize())[self.state]
        self.currentLineEdit.setText(self.inputString)

    def backspace(self):
        self.currentLineEdit.backspace()
        self.inputString = self.inputString[:-1]

    def emitInputString(self):
        self.sigInputString.emit(self.inputString)

    def emitCancel(self):
        self.sigInputString.emit()

    def sizeHint(self):
        return QSize(480, 272)
    
    def terminate(self):
        self.close

class ClickableLineEdit(QLineEdit):  # need this to know which line edit were on
    clicked = pyqtSignal(QLineEdit)  # signal when the text entry is left clicked

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        QLineEdit.mousePressEvent(self, event)

#TODO add comments
