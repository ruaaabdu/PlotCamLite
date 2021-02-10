# KEYBOARD CLASS

# PyQt Widgets for the applicaton and layout
from PyQt5.QtWidgets import QApplication, QWidget, \
    QGroupBox, QVBoxLayout, QPushButton, QGridLayout, QLabel,\
    QDialog, QMainWindow, QErrorMessage, QHBoxLayout, QLineEdit, QSizePolicy, QMessageBox
# PyQt GUI for GUI components
from PyQt5.QtGui import QIcon, QImage, QPixmap
# PyQt UIC for UI methods
from PyQt5.uic import loadUi

from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QSize

class InputState:
    LOWER = 0
    CAPITAL = 1

class KeyButton(QPushButton):
    sigKeyButtonClicked = pyqtSignal()

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(50, 50)
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
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "m"],
            ["z", "x", "c", "v", "b", "n", "_", ".", "/", " "],
        ]
        self.inputString = "" ## resetting input
        self.state = InputState.LOWER

        self.stateButton = QPushButton()
        self.stateButton.setText("Caps")
        self.backButton = QPushButton()
        self.backButton.setText("Delete")
        self.okButton = QPushButton()
        self.okButton.setText("Enter")
        self.cancelButton = QPushButton()
        self.cancelButton.setText("Cancel")

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
                self.getButtonByKey(key).sigKeyButtonClicked.connect(
                    lambda v=key: self.addInputByKey(v)
                )
                self.keysLayout.setColumnMinimumWidth(keyIndex, 50)
            self.keysLayout.setRowMinimumHeight(lineIndex, 50)
        
        self.stateButton.setCheckable(True) 
        self.stateButton.clicked.connect(self.switchState)
        self.backButton.clicked.connect(self.backspace)
        self.okButton.clicked.connect(self.emitInputString)
        self.cancelButton.clicked.connect(self.emitCancel)

        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.backButton)
        self.buttonLayout.addWidget(self.stateButton)
        self.buttonLayout.addWidget(self.okButton)

        #self.globalLayout.addWidget(self.currentLineEdit)
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

        #if self.currentLineEdit and (self.currentLineEdit.text().isspace() or not self.currentLineEdit.text()): # clicked on another line edit, but the past line edit is empty. revert to default string
        #    self.currentLineEdit.setText(self.currentLineEdit.default_text)

        # updating new line edit
        self.currentLineEdit = line_edit 
        #if self.currentLineEdit.text() == self.currentLineEdit.default_text:
        #    self.currentLineEdit.setText("")

        self.inputString = self.currentLineEdit.text()


    def switchState(self):
        self.state = not self.state

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
